from django.urls import path
from . import views
from accounts.views import UserAPIView

urlpatterns = [
    path('', views.task_lists_view, name='task_lists'),
    path('list/<int:list_id>/', views.task_list_detail_view, name='task_list_detail'),
    path('api/tasklists/', views.TaskListAPIView.as_view(), name='tasklist_api'),
    path('api/tasklists/<int:pk>/', views.TaskListAPIView.as_view(), name='tasklist_detail_api'),
    path('api/tasks/', views.TaskAPIView.as_view(), name='task_api'),
    path('api/tasks/<int:pk>/', views.TaskDetail.as_view(), name='task_detail_api'),
    path('api/users/', UserAPIView.as_view(), name='user-list'),
]
