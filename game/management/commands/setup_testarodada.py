# Em: game/management/commands/setup_e_testa_rodada.py

from django.core.management.base import BaseCommand
from django.db import transaction
from game.models import *
from django.contrib.auth.models import User
from decimal import Decimal
import json
from game.services.controle_rodada import processar_rodada_atual

class Command(BaseCommand):
    help = 'Cria um cenário de teste com custos de produção variáveis por empresa.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- INICIANDO SETUP COMPLETO ---'))

        # 1. Limpeza
        self.stdout.write('Limpando banco de dados...')
        Partida.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Produto.objects.all().delete()
        CustoProducao.objects.all().delete() # Limpa a nova tabela também
        CustoTransporte.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Banco de dados limpo.'))

        # 2. Criação de Usuários e Produtos
        self.stdout.write('Criando usuários e produtos...')
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
        yuri_user, _ = User.objects.get_or_create(username='yuri')
        vini_user, _ = User.objects.get_or_create(username='vinicius')
        
        p1 = Produto.objects.create(nome='Cafeteira', preco=Decimal('150.00'), quantidade=1000, categoria='Eletro')
        p2 = Produto.objects.create(nome='Torradeira', preco=Decimal('90.00'), quantidade=1000, categoria='Eletro')
        self.stdout.write(self.style.SUCCESS('Usuários e Produtos criados.'))
        
        # 2.1 POPULANDO CUSTOS DE PRODUÇÃO
        self.stdout.write('Populando custos de produção por empresa...')
        CustoProducao.objects.create(nome_empresa_template='Empresa A', produto=p1, custo_unitario=Decimal('30.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa A', produto=p2, custo_unitario=Decimal('40.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa B', produto=p1, custo_unitario=Decimal('29.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa B', produto=p2, custo_unitario=Decimal('41.00'))
        # Adicionar aqui os custos para as Empresas C e D se for testá-las.
        self.stdout.write(self.style.SUCCESS('Custos de produção populados.'))

        # 3. Criação da Partida e Jogadores
        self.stdout.write('Criando partida e jogadores...')
        partida_obj = Partida.objects.create(nome='Partida Teste TCC', admin=admin_user, status='INICIADA')
        jp1 = JogadorPartida.objects.create(partida=partida_obj, jogador=yuri_user, nome_empresa_jogador='Empresa A', cd_origem_principal_jogador='Unidade 1')
        jp2 = JogadorPartida.objects.create(partida=partida_obj, jogador=vini_user, nome_empresa_jogador='Empresa B', cd_origem_principal_jogador='Unidade 1')
        self.stdout.write(self.style.SUCCESS(f"Partida '{partida_obj.nome}' criada."))

        # 4. Criação dos Dados da Rodada
        self.stdout.write('Configurando dados da Rodada 1...')
        rodada_obj = Rodada.objects.create(partida=partida_obj, numero=1, ativo=True)
        rodada_obj.produto_demandado = p2 # Testando com Torradeira
        rodada_obj.quantidade_demandada = 80
        rodada_obj.destino_demanda = 'Osasco'
        rodada_obj.save()

        # Populando custos de transport
        CustoTransporte.objects.get_or_create(nome_empresa_template='Empresa A', cd_origem='Unidade 1', local_destino='Osasco', produto=p2, defaults={'custo_unitario_transporte':Decimal('2.00')})
        CustoTransporte.objects.get_or_create(nome_empresa_template='Empresa B', cd_origem='Unidade 1', local_destino='Osasco', produto=p2, defaults={'custo_unitario_transporte':Decimal('2.00')})

        # Configurando estoques e decisões
        EstoqueJogador.objects.get_or_create(jogador_partida=jp1, produto=p2, defaults={'quantidade': 80})
        EstoqueJogador.objects.get_or_create(jogador_partida=jp2, produto=p2, defaults={'quantidade': 50})
        
        # Exemplo: Nenhum jogador decide produzir, eles vão vender do estoque inicial.
        Decisao.objects.get_or_create(jogador=yuri_user, partida=partida_obj, rodada=rodada_obj, produto=p2, defaults={'quantidade_produzida': 0, 'preco_unitario': Decimal('55.00')})
        Decisao.objects.get_or_create(jogador=vini_user, partida=partida_obj, rodada=rodada_obj, produto=p2, defaults={'quantidade_produzida': 0, 'preco_unitario': Decimal('54.00')}) # Melhor preço
        
        self.stdout.write(self.style.SUCCESS('Dados da Rodada 1 configurados.'))

        # 5. Processamento e Exibição do Resultado
        self.stdout.write(self.style.WARNING('\n--- PROCESSANDO A RODADA ---'))
        processar_rodada_atual(rodada_obj)
        self.stdout.write(self.style.SUCCESS('Processamento concluído.'))

        rodada_obj.refresh_from_db()
        self.stdout.write(self.style.WARNING('\n--- RESULTADO FINAL DA RODADA 1 ---'))
        self.stdout.write(json.dumps(rodada_obj.resultados, indent=4, ensure_ascii=False))
