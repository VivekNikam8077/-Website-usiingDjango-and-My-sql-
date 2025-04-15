from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.urls import reverse
from django.contrib.auth.models import User

@ensure_csrf_cookie
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Get next URL or default to index
                next_url = request.POST.get('next', '')
                if next_url and next_url != 'None':
                    return redirect(next_url)
                else:
                    return redirect('polls:index')
            else:
                # If authentication failed but user exists, it might be due to department restrictions
                try:
                    user_obj = User.objects.get(username=username)
                    if user_obj and not (user_obj.is_staff or user_obj.is_superuser):
                        messages.error(request, "Your account is not properly set up. Please contact an administrator.")
                    else:
                        messages.error(request, "Invalid username or password.")
                except User.DoesNotExist:
                    messages.error(request, "Invalid username or password.")
                    
        # Form is invalid, but we're rendering our own template
        # so errors will be shown via the form.errors
    else:
        form = AuthenticationForm()
    return render(request, 'polls/login.html', {'form': form})

@ensure_csrf_cookie
@csrf_protect
def signup_view(request):
    # Disable direct signup - users should be created by administrators
    messages.error(request, "Direct sign-ups are disabled. Please contact an administrator to create an account.")
    return redirect('login')
    
    # The code below is kept but not used - you can enable it if you want to allow public signup
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Don't automatically log in - wait for admin to assign department
            messages.success(request, 'Account created successfully! An administrator will review your account.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'polls/signup.html', {'form': form})
    """

@login_required
@csrf_protect
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('polls:index') 