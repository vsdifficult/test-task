from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"
