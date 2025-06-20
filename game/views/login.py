from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Se já está logado, manda para o dashboard
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('password')

        user = authenticate(request, username=usuario, password=senha)
        
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('painel_admin') 
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return redirect('login')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('home')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard') # Se já está logado, manda para o dashboard
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password_confirmation')

        if pass1 != pass2:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O nome de usuário "{username}" já está em uso.')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=pass1)
        user.save()
        
        messages.success(request, f'Usuário "{username}" criado com sucesso! Faça o login.')
        return redirect('login')

    return render(request, 'register.html')