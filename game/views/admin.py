from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from game.models import Partida
from game.services.controle_rodada import avancar_rodada  # continua aqui

@staff_member_required
def admin_view(request):
    if request.method == "POST":
        # Criação de nova partida
        nome = request.POST.get("nome_partida")
        if nome:
            Partida.objects.create(nome=nome)
            messages.success(request, f"Partida '{nome}' criada com sucesso.")
            return redirect("admin")

        # Avançar rodada de uma partida existente
        partida_id = request.POST.get("avancar_rodada")
        if partida_id:
            try:
                partida = Partida.objects.get(id=partida_id)
                nova_rodada = avancar_rodada(partida)

                if nova_rodada is None:
                    messages.warning(request, f"Não é possível avançar a rodada da partida '{partida.nome}' porque nem todos os jogadores tomaram decisão ainda.")
                else:
                    messages.success(request, f"Rodada {nova_rodada.numero} da partida '{partida.nome}' iniciada com sucesso.")

            except Partida.DoesNotExist:
                messages.error(request, "Partida não encontrada.")

            return redirect("admin")

    partidas = Partida.objects.all().order_by('-data_inicio')

    partidas_info = []
    for partida in partidas:
        rodada_ativa = partida.rodada_set.filter(ativo=True).first()
        jogadores = partida.jogadores.all()
        pode_avancar = True

        if rodada_ativa:
            for jogador in jogadores:
                if not jogador.decisao_set.filter(rodada=rodada_ativa).exists():
                    pode_avancar = False
                    break

        partidas_info.append({
            'partida': partida,
            'rodada_ativa': rodada_ativa,
            'pode_avancar': pode_avancar,
        })

    return render(request, 'admin.html', {
        'partidas_info': partidas_info,
        'usuario': request.user,
    })