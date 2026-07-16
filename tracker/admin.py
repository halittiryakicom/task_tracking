from django.contrib import admin

from .models import Category, Person, ProgressLog, Role, Task


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
	list_display = ('name', 'created_at')
	search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'parent', 'order')
	list_filter = ('parent',)
	search_fields = ('name', 'description')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
	list_display = (
		'title',
		'plan_date',
		'weekday',
		'responsible',
		'worker',
		'section',
		'priority',
		'is_completed',
		'due_date',
	)
	list_filter = ('section', 'priority', 'is_completed', 'plan_date', 'category', 'responsible', 'worker')
	search_fields = ('title', 'details', 'owner_group', 'responsible__name', 'worker__name')
	autocomplete_fields = ('category', 'responsible', 'worker')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ('name', 'role', 'created_at')
	list_filter = ('role',)
	search_fields = ('name', 'role__name')
	autocomplete_fields = ('role',)


@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
	list_display = ('task', 'created_at')
	search_fields = ('task__title', 'note')
	autocomplete_fields = ('task',)
