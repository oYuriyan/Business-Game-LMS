from django.core.management.base import BaseCommand
from django.db import transaction
from game.models import *
from django.contrib.auth.models import User
from decimal import Decimal
import json
from game.services.controle_rodada import processar_rodada_atual

class Command(BaseCommand):
    help = 'Limpa o BD, cria um cenário de teste completo, processa a rodada 1 e imprime o resultado.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- INICIANDO SETUP COMPLETO ---'))

        # 1. Limpeza
        self.stdout.write('Limpando banco de dados...')
        Partida.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Produto.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Banco de dados limpo.'))

        # 2. Criação de Usuários e Produtos
        self.stdout.write('Criando usuários e produtos...')
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'is_staff': True, 'is_superuser': True})
        yuri_user, _ = User.objects.get_or_create(username='yuri')
        vini_user, _ = User.objects.get_or_create(username='vinicius')
        
        p1 = Produto.objects.create(nome='Cafeteira', preco=Decimal('150.00'), quantidade=1000, categoria='Eletro', custo_producao_unitario=Decimal('75.00'))
        p2 = Produto.objects.create(nome='Torradeira', preco=Decimal('90.00'), quantidade=1000, categoria='Eletro', custo_producao_unitario=Decimal('40.00'))
        self.stdout.write(self.style.SUCCESS('Usuários e Produtos criados.'))

        # 3. Criação da Partida e Jogadores
        self.stdout.write('Criando partida e jogadores...')
        partida_obj = Partida.objects.create(nome='Partida Teste TCC', admin=admin_user)
        jp1 = JogadorPartida.objects.create(partida=partida_obj, jogador=yuri_user, nome_empresa_jogador='Empresa A', cd_origem_principal_jogador='CD Sao Paulo')
        jp2 = JogadorPartida.objects.create(partida=partida_obj, jogador=vini_user, nome_empresa_jogador='Empresa B', cd_origem_principal_jogador='CD Rio de Janeiro')
        self.stdout.write(self.style.SUCCESS(f"Partida '{partida_obj.nome}' criada."))

        # 4. Criação dos Dados da Rodada
        self.stdout.write('Configurando dados da Rodada 1...')
        rodada_obj = Rodada.objects.create(partida=partida_obj, numero=1, ativo=True)
        rodada_obj.produto_demandado = p1
        rodada_obj.quantidade_demandada = 80
        rodada_obj.destino_demanda = 'Osasco'
        rodada_obj.save()
        CustoTransporte.objects.get_or_create(nome_empresa_template='Empresa A', cd_origem='CD Sao Paulo', local_destino='Osasco', produto=p1, defaults={'custo_unitario_transporte':Decimal('5.50')})
        CustoTransporte.objects.get_or_create(nome_empresa_template='Empresa B', cd_origem='CD Rio de Janeiro', local_destino='Osasco', produto=p1, defaults={'custo_unitario_transporte':Decimal('8.00')})
        EstoqueJogador.objects.get_or_create(jogador_partida=jp1, produto=p1, defaults={'quantidade': 100})
        EstoqueJogador.objects.get_or_create(jogador_partida=jp2, produto=p1, defaults={'quantidade': 100})
        Decisao.objects.get_or_create(jogador=yuri_user, partida=partida_obj, rodada=rodada_obj, produto=p1, defaults={'quantidade_produzida': 50, 'preco_unitario': Decimal('130.00')})
        Decisao.objects.get_or_create(jogador=vini_user, partida=partida_obj, rodada=rodada_obj, produto=p1, defaults={'quantidade_produzida': 40, 'preco_unitario': Decimal('125.00')})
        self.stdout.write(self.style.SUCCESS('Dados da Rodada 1 configurados.'))

        # 5. Processamento e Exibição do Resultado
        self.stdout.write(self.style.WARNING('\n--- PROCESSANDO A RODADA ---'))
        processar_rodada_atual(rodada_obj)
        self.stdout.write(self.style.SUCCESS('Processamento concluído.'))

        rodada_obj.refresh_from_db()
        self.stdout.write(self.style.WARNING('\n--- RESULTADO FINAL DA RODADA 1 ---'))
        self.stdout.write(json.dumps(rodada_obj.resultados, indent=4, ensure_ascii=False))

