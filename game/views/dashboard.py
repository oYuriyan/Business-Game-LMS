from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# View que exibe o painel inicial do usuário após login
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html', {
        'usuario': request.user,
        'mensagem': 'Bem-vindo ao Business Game!'
    })