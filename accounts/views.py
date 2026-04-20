from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from .forms import UserRegistrationForm, UserLoginForm
from .models import User


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome aboard.")
            return redirect('dashboard')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = UserLoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_id = form.cleaned_data['login_id']
            password = form.cleaned_data['password']

            # Try login by phone_number (which is our username)
            user = authenticate(request, username=login_id, password=password)

            if not user:
                # Try search by business_name
                try:
                    user_obj = User.objects.get(business_name=login_id)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.business_name}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid credentials. Please try again.")
        return render(request, 'accounts/login.html', {'form': form})


class ProfileUpdateView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        user = request.user
        user.business_name = request.POST.get('business_name', user.business_name)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.email = request.POST.get('email', user.email)
        user.address = request.POST.get('address', user.address)
        user.username = user.phone_number  # keep in sync
        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
