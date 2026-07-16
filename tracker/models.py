from django.db import models
from django.utils import timezone


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	parent = models.ForeignKey(
		'self',
		on_delete=models.CASCADE,
		null=True,
		blank=True,
		related_name='children',
	)
	description = models.TextField(blank=True)
	order = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ['order', 'name']
		verbose_name = 'Kategori'
		verbose_name_plural = 'Kategoriler'

	def __str__(self):
		if self.parent:
			return f"{self.parent.name} / {self.name}"
		return self.name


class Role(models.Model):
	name = models.CharField('Rol adı', max_length=80, unique=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['name']
		verbose_name = 'Rol'
		verbose_name_plural = 'Roller'

	def __str__(self):
		return self.name


class Person(models.Model):
	name = models.CharField('Ad soyad', max_length=120, unique=True)
	role = models.ForeignKey(
		Role,
		on_delete=models.PROTECT,
		null=True,
		blank=True,
		related_name='people',
		verbose_name='Rol',
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['role__name', 'name']
		verbose_name = 'Kişi'
		verbose_name_plural = 'Kişiler'

	def __str__(self):
		return f"{self.name} ({self.role.name if self.role_id else 'Rol yok'})"


class Task(models.Model):
	class Section(models.TextChoices):
		DEADLINE = 'SON_TESLIM_GUNU', 'Son teslim günü'
		PLANNED = 'YAPILMASI_PLANLANANLAR', 'Yapılması planlananlar'

	class Priority(models.TextChoices):
		LOW = 'LOW', 'Düşük'
		MEDIUM = 'MEDIUM', 'Orta'
		HIGH = 'HIGH', 'Yüksek'
		CRITICAL = 'CRITICAL', 'Kritik'

	WEEKDAY_TR = {
		0: 'Pazartesi',
		1: 'Salı',
		2: 'Çarşamba',
		3: 'Perşembe',
		4: 'Cuma',
		5: 'Cumartesi',
		6: 'Pazar',
	}

	plan_date = models.DateField('Plan tarihi', default=timezone.localdate)
	weekday = models.CharField('Gün', max_length=20, blank=True)
	owner_group = models.CharField('İş alanı / sorumlu', max_length=150, blank=True)
	category = models.ForeignKey(
		Category,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='tasks',
		verbose_name='Kategori',
	)
	responsible = models.ForeignKey(
		Person,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='responsible_tasks',
		verbose_name='Sorumlu',
	)
	worker = models.ForeignKey(
		Person,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='worker_tasks',
		verbose_name='İş Alan',
	)
	section = models.CharField('Bölüm', max_length=30, choices=Section.choices)
	title = models.CharField('Başlık', max_length=200)
	details = models.TextField('Detay', blank=True)
	due_date = models.DateField('Son teslim tarihi', null=True, blank=True)
	priority = models.CharField(
		'Öncelik',
		max_length=10,
		choices=Priority.choices,
		default=Priority.MEDIUM,
	)
	is_completed = models.BooleanField('Tamamlandı', default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-plan_date', 'is_completed', '-due_date', '-created_at']
		verbose_name = 'İş kaydı'
		verbose_name_plural = 'İş kayıtları'

	def save(self, *args, **kwargs):
		self.weekday = self.WEEKDAY_TR.get(self.plan_date.weekday(), '')
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.plan_date} - {self.title}"


class ProgressLog(models.Model):
	task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress_logs', verbose_name='Görev')
	note = models.TextField('İlerleme notu')
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']
		verbose_name = 'İlerleme kaydı'
		verbose_name_plural = 'İlerleme kayıtları'

	def __str__(self):
		return f"{self.task.title} - {timezone.localtime(self.created_at).strftime('%d.%m.%Y %H:%M')}"
