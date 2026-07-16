import json
from datetime import date

from django.db.models import Count, Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from .models import Category, Person, ProgressLog, Role, Task


def _json_error(message, status=400):
	return JsonResponse({'ok': False, 'error': message}, status=status)


def _parse_body(request):
	if not request.body:
		return {}
	try:
		return json.loads(request.body.decode('utf-8'))
	except json.JSONDecodeError:
		return None


def _parse_date(value, fallback=None):
	if not value:
		return fallback
	try:
		return date.fromisoformat(value)
	except (TypeError, ValueError):
		return fallback


def _serialize_person(person):
	return {
		'id': person.id,
		'name': person.name,
		'role_id': person.role_id,
		'role_name': person.role.name if person.role_id else '',
	}


def _serialize_role(role):
	return {
		'id': role.id,
		'name': role.name,
		'people_count': getattr(role, 'people_count', 0),
	}


def _serialize_category(category):
	return {
		'id': category.id,
		'name': category.name,
		'parent_id': category.parent_id,
		'parent_name': category.parent.name if category.parent_id else '',
		'description': category.description,
		'order': category.order,
		'task_count': getattr(category, 'task_count', 0),
		'child_count': getattr(category, 'child_count', 0),
	}


def _serialize_progress(log):
	local_created = timezone.localtime(log.created_at)
	return {
		'id': log.id,
		'note': log.note,
		'created_at': local_created.isoformat(),
		'created_at_label': local_created.strftime('%d.%m.%Y %H:%M'),
	}


def _serialize_task(task, include_logs=False):
	data = {
		'id': task.id,
		'title': task.title,
		'details': task.details,
		'plan_date': task.plan_date.isoformat() if task.plan_date else '',
		'plan_date_label': task.plan_date.strftime('%d.%m.%Y') if task.plan_date else '',
		'weekday': task.weekday,
		'due_date': task.due_date.isoformat() if task.due_date else '',
		'due_date_label': task.due_date.strftime('%d.%m.%Y') if task.due_date else '',
		'priority': task.priority,
		'priority_display': task.get_priority_display(),
		'section': task.section,
		'section_display': task.get_section_display(),
		'is_completed': task.is_completed,
		'category_id': task.category_id,
		'category_name': str(task.category) if task.category_id else '',
		'responsible_id': task.responsible_id,
		'responsible_name': task.responsible.name if task.responsible_id else '',
		'worker_id': task.worker_id,
		'worker_name': task.worker.name if task.worker_id else '',
		'worker_role_id': task.worker.role_id if task.worker_id else None,
		'worker_role_name': task.worker.role.name if task.worker_id and task.worker.role_id else '',
		'owner_group': task.owner_group,
		'created_at_label': timezone.localtime(task.created_at).strftime('%d.%m.%Y %H:%M'),
		'updated_at_label': timezone.localtime(task.updated_at).strftime('%d.%m.%Y %H:%M'),
	}
	if include_logs:
		data['progress_logs'] = [_serialize_progress(log) for log in task.progress_logs.all()]
	return data


def _task_stats():
	today = timezone.localdate()
	queryset = Task.objects.all()
	return {
		'total': queryset.count(),
		'open': queryset.filter(is_completed=False).count(),
		'completed': queryset.filter(is_completed=True).count(),
		'overdue': queryset.filter(is_completed=False, due_date__lt=today).count(),
		'categories': Category.objects.count(),
		'people': Person.objects.count(),
	}


def _category_stats():
	return {
		'total': Category.objects.count(),
		'root': Category.objects.filter(parent__isnull=True).count(),
		'child': Category.objects.filter(parent__isnull=False).count(),
		'linked_tasks': Task.objects.exclude(category__isnull=True).count(),
	}


def _choices_payload():
	return {
		'sections': [{'value': value, 'label': label} for value, label in Task.Section.choices],
		'priorities': [{'value': value, 'label': label} for value, label in Task.Priority.choices],
	}


def _task_queryset(include_logs=False):
	queryset = Task.objects.select_related('category', 'responsible', 'worker')
	if include_logs:
		queryset = queryset.prefetch_related(Prefetch('progress_logs', queryset=ProgressLog.objects.order_by('-created_at')))
	return queryset.order_by('-plan_date', 'is_completed', '-updated_at')


def _role_queryset():
	return Role.objects.annotate(people_count=Count('people', distinct=True)).order_by('name')


def _category_queryset():
	return Category.objects.select_related('parent').annotate(
		task_count=Count('tasks', distinct=True),
		child_count=Count('children', distinct=True),
	).order_by('order', 'name')


def _resolve_person(person_id):
	if not person_id:
		return None
	person = Person.objects.select_related('role').filter(pk=person_id).first()
	if person is None:
		raise ValueError('Seçilen kişi bulunamadı.')
	return person


def _resolve_role(role_id):
	if not role_id:
		raise ValueError('Rol seçimi zorunludur.')
	role = Role.objects.filter(pk=role_id).first()
	if role is None:
		raise ValueError('Seçilen rol bulunamadı.')
	return role


def _apply_task_payload(task, payload):
	if not payload.get('title', '').strip():
		raise ValueError('Görev başlığı zorunludur.')

	section = payload.get('section') or Task.Section.PLANNED
	priority = payload.get('priority') or Task.Priority.MEDIUM
	if section not in {value for value, _ in Task.Section.choices}:
		raise ValueError('Geçersiz bölüm seçildi.')
	if priority not in {value for value, _ in Task.Priority.choices}:
		raise ValueError('Geçersiz öncelik seçildi.')

	category = None
	category_id = payload.get('category_id')
	if category_id:
		category = Category.objects.filter(pk=category_id).first()
		if category is None:
			raise ValueError('Seçilen kategori bulunamadı.')

	plan_date = _parse_date(payload.get('plan_date'), timezone.localdate())
	if not plan_date:
		raise ValueError('Geçerli bir plan tarihi girin.')

	task.plan_date = plan_date
	task.owner_group = (payload.get('owner_group') or '').strip()
	task.category = category
	task.responsible = _resolve_person(payload.get('responsible_id'))
	task.worker = _resolve_person(payload.get('worker_id'))
	task.section = section
	task.title = payload.get('title', '').strip()
	task.details = (payload.get('details') or '').strip()
	task.due_date = _parse_date(payload.get('due_date'))
	task.priority = priority
	task.is_completed = bool(payload.get('is_completed', False))
	task.save()
	return task


@ensure_csrf_cookie
def spa_shell(request):
	return render(request, 'tracker/spa.html', {})


def legacy_redirect(request, *args, **kwargs):
	return redirect('tracker:task_list')


@require_GET
def api_bootstrap(request):
	return JsonResponse({
		'ok': True,
		'tasks': [_serialize_task(task) for task in _task_queryset()],
		'categories': [_serialize_category(category) for category in _category_queryset()],
		'roles': [_serialize_role(role) for role in _role_queryset()],
		'people': [_serialize_person(person) for person in Person.objects.select_related('role').all()],
		'stats': _task_stats(),
		'category_stats': _category_stats(),
		'choices': _choices_payload(),
		'today': timezone.localdate().isoformat(),
	})


@require_http_methods(['GET', 'POST'])
def api_tasks(request):
	if request.method == 'GET':
		return JsonResponse({'ok': True, 'tasks': [_serialize_task(task) for task in _task_queryset()]})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	try:
		task = _apply_task_payload(Task(), payload)
	except ValueError as exc:
		return _json_error(str(exc))

	task = _task_queryset(include_logs=True).get(pk=task.pk)
	return JsonResponse({'ok': True, 'task': _serialize_task(task, include_logs=True), 'stats': _task_stats()}, status=201)


@require_http_methods(['GET', 'PATCH', 'DELETE'])
def api_task_detail(request, pk):
	task = get_object_or_404(_task_queryset(include_logs=True), pk=pk)

	if request.method == 'GET':
		return JsonResponse({'ok': True, 'task': _serialize_task(task, include_logs=True)})

	if request.method == 'DELETE':
		task.delete()
		return JsonResponse({'ok': True, 'stats': _task_stats()})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	try:
		task = _apply_task_payload(task, payload)
	except ValueError as exc:
		return _json_error(str(exc))

	task = _task_queryset(include_logs=True).get(pk=task.pk)
	return JsonResponse({'ok': True, 'task': _serialize_task(task, include_logs=True), 'stats': _task_stats()})


@require_http_methods(['POST'])
def api_task_logs(request, pk):
	task = get_object_or_404(Task, pk=pk)
	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	note = (payload.get('note') or '').strip()
	if not note:
		return _json_error('İlerleme notu boş bırakılamaz.')

	log = ProgressLog.objects.create(task=task, note=note)
	task = _task_queryset(include_logs=True).get(pk=task.pk)
	return JsonResponse({'ok': True, 'log': _serialize_progress(log), 'task': _serialize_task(task, include_logs=True)})


@require_http_methods(['GET', 'POST'])
def api_categories(request):
	if request.method == 'GET':
		return JsonResponse({
			'ok': True,
			'categories': [_serialize_category(category) for category in _category_queryset()],
			'category_stats': _category_stats(),
		})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	if not name:
		return _json_error('Kategori adı zorunludur.')

	parent = None
	parent_id = payload.get('parent_id')
	if parent_id:
		parent = Category.objects.filter(pk=parent_id).first()
		if parent is None:
			return _json_error('Seçilen üst kategori bulunamadı.')

	category = Category.objects.create(
		name=name,
		parent=parent,
		description=(payload.get('description') or '').strip(),
		order=int(payload.get('order') or 0),
	)
	category = _category_queryset().get(pk=category.pk)
	return JsonResponse({'ok': True, 'category': _serialize_category(category), 'category_stats': _category_stats()}, status=201)


@require_http_methods(['PATCH', 'DELETE'])
def api_category_detail(request, pk):
	category = get_object_or_404(Category, pk=pk)

	if request.method == 'DELETE':
		if category.children.exists():
			return _json_error('Alt kategorisi olan kayıt silinemez.')
		category.delete()
		return JsonResponse({'ok': True, 'category_stats': _category_stats()})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	if not name:
		return _json_error('Kategori adı zorunludur.')

	parent = None
	parent_id = payload.get('parent_id')
	if parent_id:
		parent = Category.objects.filter(pk=parent_id).exclude(pk=category.pk).first()
		if parent is None:
			return _json_error('Seçilen üst kategori bulunamadı.')

	category.name = name
	category.parent = parent
	category.description = (payload.get('description') or '').strip()
	category.order = int(payload.get('order') or 0)
	category.save()
	category = _category_queryset().get(pk=category.pk)
	return JsonResponse({'ok': True, 'category': _serialize_category(category), 'category_stats': _category_stats()})


@require_http_methods(['GET', 'POST'])
def api_people(request):
	if request.method == 'GET':
		return JsonResponse({'ok': True, 'people': [_serialize_person(person) for person in Person.objects.select_related('role').all()], 'stats': _task_stats()})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	role_id = payload.get('role_id')
	if not name:
		return _json_error('Kişi adı zorunludur.')

	try:
		role = _resolve_role(role_id)
	except ValueError as exc:
		return _json_error(str(exc))

	person = Person.objects.create(name=name, role=role)
	person = Person.objects.select_related('role').get(pk=person.pk)
	return JsonResponse({'ok': True, 'person': _serialize_person(person), 'stats': _task_stats()}, status=201)


@require_http_methods(['PATCH', 'DELETE'])
def api_person_detail(request, pk):
	person = get_object_or_404(Person, pk=pk)

	if request.method == 'DELETE':
		person.delete()
		return JsonResponse({'ok': True, 'stats': _task_stats()})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	role_id = payload.get('role_id')
	if not name:
		return _json_error('Kişi adı zorunludur.')

	try:
		role = _resolve_role(role_id)
	except ValueError as exc:
		return _json_error(str(exc))

	person.name = name
	person.role = role
	person.save()
	person = Person.objects.select_related('role').get(pk=person.pk)
	return JsonResponse({'ok': True, 'person': _serialize_person(person), 'stats': _task_stats()})


@require_http_methods(['GET', 'POST'])
def api_roles(request):
	if request.method == 'GET':
		return JsonResponse({'ok': True, 'roles': [_serialize_role(role) for role in _role_queryset()]})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	if not name:
		return _json_error('Rol adı zorunludur.')
	if Role.objects.filter(name__iexact=name).exists():
		return _json_error('Bu rol zaten mevcut.')

	role = Role.objects.create(name=name)
	role = _role_queryset().get(pk=role.pk)
	return JsonResponse({'ok': True, 'role': _serialize_role(role)}, status=201)


@require_http_methods(['PATCH', 'DELETE'])
def api_role_detail(request, pk):
	role = get_object_or_404(Role, pk=pk)

	if request.method == 'DELETE':
		if role.people.exists():
			return _json_error('Bu role bağlı kişiler var. Önce kişilerin rolünü değiştirin.')
		role.delete()
		return JsonResponse({'ok': True})

	payload = _parse_body(request)
	if payload is None:
		return _json_error('Geçersiz JSON içeriği.')

	name = (payload.get('name') or '').strip()
	if not name:
		return _json_error('Rol adı zorunludur.')
	if Role.objects.filter(name__iexact=name).exclude(pk=role.pk).exists():
		return _json_error('Bu rol adı başka bir kayıtta kullanılıyor.')

	role.name = name
	role.save(update_fields=['name'])
	role = _role_queryset().get(pk=role.pk)
	return JsonResponse({'ok': True, 'role': _serialize_role(role)})
