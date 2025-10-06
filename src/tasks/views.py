from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import TaskList, Task
from .serializers import TaskSerializer, TaskListSerializer
from .tasks import send_task_assigned_notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_task_update(task):
    """Helper function to send task updates via Channels."""
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        user_id = task.assigned_to.id
        task_data = TaskSerializer(task).data
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'task_update',
                'task': task_data
            }
        )

@login_required
def task_lists_view(request):
    task_lists = TaskList.objects.filter(created_by=request.user)
    return render(request, 'task_lists.html', {'task_lists': task_lists})

@login_required
def task_list_detail_view(request, list_id):
    task_list = get_object_or_404(TaskList, id=list_id, created_by=request.user)
    tasks = task_list.tasks.all()
    return render(request, 'task_list_detail.html', {'task_list': task_list, 'tasks': tasks})

class TaskListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        task_lists = TaskList.objects.filter(created_by=request.user)
        serializer = TaskListSerializer(task_lists, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskListSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                if 'UNIQUE constraint failed' in str(e):
                    return Response({'error': 'A task list with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
                raise
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            # send_task_update(task)
            # send_task_assigned_notification.delay(task.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            task = serializer.save()
            # send_task_update(task)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = get_object_or_404(Task, pk=pk, assigned_to=request.user)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
