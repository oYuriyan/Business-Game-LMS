from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from game.models import Partida, Rodada, Produto
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

@staff_member_required
def definir_demanda_rodada(request, rodada_id):
    rodada = get_object_or_404(Rodada, id=rodada_id, ativo=True) # Só para rodadas ativas
    produtos_disponiveis = Produto.objects.all() # Para o admin escolher o produto demandado

    if request.method == 'POST':
        produto_id = request.POST.get('produto_demandado')
        quantidade = request.POST.get('quantidade_demandada')
        destino = request.POST.get('destino_demanda')
        # preco_max = request.POST.get('preco_maximo_aceitavel') # Opcional

        if not produto_id or not quantidade or not destino:
            messages.error(request, "Todos os campos da demanda são obrigatórios.")
        else:
            try:
                rodada.produto_demandado = Produto.objects.get(id=produto_id)
                rodada.quantidade_demandada = int(quantidade)
                rodada.destino_demanda = destino
                # if preco_max: rodada.preco_maximo_aceitavel = Decimal(preco_max)
                rodada.save()
                messages.success(request, f"Demanda para a rodada {rodada.numero} da partida '{rodada.partida.nome}' definida com sucesso.")
                return redirect('admin')
            except Produto.DoesNotExist:
                messages.error(request, "Produto selecionado inválido.")
            except ValueError:
                 messages.error(request, "Quantidade deve ser um número.")
        
    return render(request, 'definir_demanda.html', {
        'rodada': rodada,
        'produtos_disponiveis': produtos_disponiveis
    })