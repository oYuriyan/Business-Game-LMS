from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# View para exibir o formulário de login e processar autenticação
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        senha = request.POST['senha']

        usuario = authenticate(request, username=username, password=senha)

        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')  # Redireciona para a próxima tela 
        else:
            messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')

# View para encerrar a sessão
def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        pass2 = request.POST.get('password_confirmation')

        # Validações simples
        if pass1 != pass2:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'O nome de usuário "{username}" já está em uso.')
            return redirect('register')
        
        # Cria o usuário
        user = User.objects.create_user(username=username, password=pass1)
        user.save()
        
        messages.success(request, f'Usuário "{username}" criado com sucesso! Faça o login.')
        return redirect('login')

    return render(request, 'register.html')