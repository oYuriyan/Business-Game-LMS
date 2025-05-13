from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from game.models import Partida
from game.services.controle_rodada import avancar_rodada

@staff_member_required
def admin_view(request):
    if request.method == "POST":
        # Criação de nova partida
        nome = request.POST.get("nome_partida")
        if nome:
            Partida.objects.create(nome=nome)
            messages.success(request, f"Partida '{nome}' criada com sucesso.")
            return redirect("admin_view")

        # Avançar rodada de uma partida existente
        partida_id = request.POST.get("avancar_rodada")
        if partida_id:
            try:
                partida = Partida.objects.get(id=partida_id)
                nova_rodada = avancar_rodada(partida)
                messages.success(request, f"Rodada {nova_rodada.numero_rodada} da partida '{partida.nome}' iniciada com sucesso.")
            except Partida.DoesNotExist:
                messages.error(request, "Partida não encontrada.")
            return redirect("admin_view")

    partidas = Partida.objects.all().order_by('-data_inicio')
    return render(request, 'admin.html', {
        'partidas': partidas,
        'usuario': request.user
    })