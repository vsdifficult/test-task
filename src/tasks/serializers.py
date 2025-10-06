from rest_framework import serializers
from .models import Task, TaskList
from accounts.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'telegram_username']

class TaskListSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = TaskList
        fields = ['id', 'name', 'description', 'created_by', 'created_at']
        read_only_fields = ['created_by']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), 
        source='assigned_to', 
        write_only=True, 
        required=False  # Make the field optional
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'task_list', 'assigned_to', 'assigned_to_id', 'due_date', 'completed', 'created_at', 'updated_at']

    def create(self, validated_data):
        # If assigned_to is not provided, default to the current user.
        if 'assigned_to' not in validated_data:
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                validated_data['assigned_to'] = request.user
        
        # Ensure assigned_to is set before creating the task
        if 'assigned_to' not in validated_data:
            raise serializers.ValidationError("Could not determine the user to assign the task to.")

        return super().create(validated_data)
