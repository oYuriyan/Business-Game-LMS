from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from game.models import Partida

#O decorador @staff_member_required garante que apenas usuários staff/admin acessem essa página.
@staff_member_required
def admin_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome_partida")
        if nome:
            from game.models import Partida
            Partida.objects.create(nome=nome, ativa=True)
    
    partidas = Partida.objects.all().order_by('-data_criacao')
    return render(request, 'admin_panel.html', {
        'partidas': partidas,
        'usuario': request.user
    })