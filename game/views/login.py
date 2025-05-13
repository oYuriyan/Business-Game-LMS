from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
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