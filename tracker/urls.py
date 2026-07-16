from django.urls import path

from .views import (
    api_bootstrap,
    api_categories,
    api_category_detail,
    api_people,
    api_person_detail,
    api_role_detail,
    api_roles,
    api_task_detail,
    api_task_logs,
    api_tasks,
    legacy_redirect,
    spa_shell,
)

app_name = 'tracker'

urlpatterns = [
    path('', spa_shell, name='task_list'),
    path('kategoriler/', legacy_redirect, name='category_manage'),
    path('gorev/yeni/', legacy_redirect, name='task_create'),
    path('gorev/<int:pk>/duzenle/', legacy_redirect, name='task_update'),
    path('gorev/<int:pk>/sil/', legacy_redirect, name='task_delete'),
    path('api/bootstrap/', api_bootstrap, name='api_bootstrap'),
    path('api/tasks/', api_tasks, name='api_tasks'),
    path('api/tasks/<int:pk>/', api_task_detail, name='api_task_detail'),
    path('api/tasks/<int:pk>/logs/', api_task_logs, name='api_task_logs'),
    path('api/categories/', api_categories, name='api_categories'),
    path('api/categories/<int:pk>/', api_category_detail, name='api_category_detail'),
    path('api/roles/', api_roles, name='api_roles'),
    path('api/roles/<int:pk>/', api_role_detail, name='api_role_detail'),
    path('api/people/', api_people, name='api_people'),
    path('api/people/<int:pk>/', api_person_detail, name='api_person_detail'),
]
