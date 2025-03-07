from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages


class SignUpView(CreateView):
    """
    View for user registration
    """
    form_class = SignUpForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('store:home')
    
    def form_valid(self, form):
        # Save the user first
        response = super().form_valid(form)
        # Auto-login the user after successful registration
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        messages.success(self.request, f'Welcome to Metra Project, {username}! Your account has been created successfully.')
        return response


class CustomLoginView(LoginView):
    """
    Custom login view with styled form
    """
    form_class = LoginForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Welcome back, {self.request.user.username}!')
        return response


class CustomLogoutView(LogoutView):
    """
    Custom logout view
    """
    next_page = reverse_lazy('store:home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile(request):
    """
    View for displaying user profile
    """
    return render(request, 'users/profile.html')


@login_required
def profile_update(request):
    """
    View for updating user profile
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile_update.html', context)