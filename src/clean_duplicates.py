#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmanager.settings')
django.setup()

from tasks.models import TaskList, Task
from django.db.models import Count

# Clean TaskList duplicates
duplicates = TaskList.objects.values('name', 'created_by').annotate(count=Count('id')).filter(count__gt=1)
for dup in duplicates:
    qs = TaskList.objects.filter(name=dup['name'], created_by=dup['created_by']).order_by('created_at')[1:]
    ids_to_delete = list(qs.values_list('id', flat=True))
    TaskList.objects.filter(id__in=ids_to_delete).delete()

# Clean Task duplicates
duplicates = Task.objects.values('title', 'task_list').annotate(count=Count('id')).filter(count__gt=1)
for dup in duplicates:
    qs = Task.objects.filter(title=dup['title'], task_list=dup['task_list']).order_by('created_at')[1:]
    ids_to_delete = list(qs.values_list('id', flat=True))
    Task.objects.filter(id__in=ids_to_delete).delete()

print('Duplicates cleaned')
