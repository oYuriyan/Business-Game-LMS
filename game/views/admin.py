# Em: game/views/admin.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from game.models import Partida, Rodada, JogadorPartida, Produto
from game.services.controle_rodada import avancar_rodada as avancar_rodada_service

# O decorator garante que só superusuários acessem estas páginas
# Esta é a view principal do painel do admin
@user_passes_test(lambda u: u.is_superuser)
def painel_admin(request):
    partidas = Partida.objects.all().order_by('-data_inicio')
    
    partidas_info = []
    for partida in partidas:
        rodada_ativa = Rodada.objects.filter(partida=partida, ativo=True).first()
        jogadores = JogadorPartida.objects.filter(partida=partida)
        partidas_info.append({
            'partida': partida,
            'rodada_ativa': rodada_ativa,
            'jogadores': jogadores
        })

    context = {
        'partidas_info': partidas_info
    }
    return render(request, 'admin.html', context)

# View para a PÁGINA de criar uma nova partida
@user_passes_test(lambda u: u.is_superuser)
def criar_partida_view(request):
    if request.method == 'POST':
        nome_partida = request.POST.get('nome_partida')
        if nome_partida:
            partida = Partida.objects.create(nome=nome_partida, admin=request.user)
            messages.success(request, f"Partida '{partida.nome}' criada. Agora inicie a primeira rodada.")
            return redirect('painel_admin')
    return render(request, 'criar_partida.html')

# View para a PÁGINA de definir a demanda de uma rodada
@user_passes_test(lambda u: u.is_superuser)
def definir_demanda_view(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id)
    produtos = Produto.objects.all()
    if request.method == 'POST':
        produto_id = request.POST.get('produto_id')
        quantidade = request.POST.get('quantidade')
        destino = request.POST.get('destino')
        
        rodada.produto_demandado_id = produto_id
        rodada.quantidade_demandada = quantidade
        rodada.destino_demanda = destino
        rodada.save()
        messages.success(request, f"Demanda para a rodada {rodada.numero} salva com sucesso.")
        return redirect('painel_admin')
        
    context = {
        'rodada': rodada,
        'produtos': produtos
    }
    return render(request, 'definir_demanda.html', context)

# View para o BOTÃO de avançar a rodada de uma partida
@user_passes_test(lambda u: u.is_superuser)
def avancar_rodada_view(request, partida_id):
    # Esta view só deve aceitar POST para segurança
    if request.method == 'POST':
        partida = get_object_or_404(Partida, id=partida_id)
        
        # A lógica de serviço já lida com a criação da primeira rodada ou avanço das subsequentes
        resultado_rodada = avancar_rodada_service(partida)
        
        if resultado_rodada is None:
            messages.warning(request, f"Não foi possível avançar a rodada da partida '{partida.nome}'. Verifique se todos os jogadores já tomaram suas decisões.")
        else:
            messages.success(request, f"Rodada processada. Rodada {resultado_rodada.numero} iniciada com sucesso para a partida '{partida.nome}'.")

    # Sempre redireciona de volta para o painel
    return redirect('painel_admin')