from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "telegram_id", "telegram_username", "password1", "password2")

class TelegramLinkForm(forms.Form):
    telegram_id = forms.CharField(label="Telegram Linking Code", max_length=100)
