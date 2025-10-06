from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, TelegramLinkForm
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('task_lists')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('task_lists')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = TelegramLinkForm(request.POST)
        if form.is_valid():
            telegram_id = form.cleaned_data['telegram_id']
            request.user.telegram_id = telegram_id
            request.user.save()
            messages.success(request, 'Telegram account linked successfully!')
            return redirect('profile')
    else:
        form = TelegramLinkForm()
    return render(request, 'profile.html', {'form': form})

class UserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        username = request.query_params.get('username', None)
        users = CustomUser.objects.none()  # Start with an empty queryset

        if username:
            users = CustomUser.objects.filter(username__icontains=username)

        # If the specific query returned no results, return all users to help with debugging.
        if not users.exists():
            users = CustomUser.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
