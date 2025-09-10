from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect authenticated users

    errors = {}
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            errors['invalid'] = "Invalid username or password."

    return render(request, 'accounts/login.html', {'errors': errors})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')
