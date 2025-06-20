from django.core.management.base import BaseCommand
from django.db import transaction
from game.models import *
from django.contrib.auth.models import User
from decimal import Decimal
import json
from game.services.controle_rodada import processar_rodada_atual

class Command(BaseCommand):
    help = 'Cria um cenário de teste com custos de produção variáveis e setup granular.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('--- INICIANDO SETUP COMPLETO ---'))

        # 1. Limpeza
        self.stdout.write('Limpando banco de dados...')
        Partida.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Produto.objects.all().delete()
        CustoProducao.objects.all().delete()
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
        
        # 2.1 Populando Custos de Produção
        self.stdout.write('Populando custos de produção por empresa...')
        CustoProducao.objects.create(nome_empresa_template='Empresa A', produto=p1, custo_unitario=Decimal('30.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa A', produto=p2, custo_unitario=Decimal('40.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa B', produto=p1, custo_unitario=Decimal('29.00'))
        CustoProducao.objects.create(nome_empresa_template='Empresa B', produto=p2, custo_unitario=Decimal('41.00'))
        self.stdout.write(self.style.SUCCESS('Custos de produção populados.'))

        # 3. Criação da Partida e Jogadores (COM A CORREÇÃO)
        self.stdout.write('Criando partida e jogadores...')
        partida_obj = Partida.objects.create(nome='Partida Teste TCC', admin=admin_user, status='INICIADA')
        # A criação agora é mais simples, sem o campo antigo
        jp1 = JogadorPartida.objects.create(partida=partida_obj, jogador=yuri_user, nome_empresa_jogador='Empresa A')
        jp2 = JogadorPartida.objects.create(partida=partida_obj, jogador=vini_user, nome_empresa_jogador='Empresa B')
        self.stdout.write(self.style.SUCCESS(f"Partida '{partida_obj.nome}' criada."))

        # O restante do script continua igual, pois depende da lógica que já atualizamos nas views
        # (A lógica de criar as Unidades, por exemplo, está na entrar_partida_view, não aqui)
        
        self.stdout.write(self.style.SUCCESS('\nSetup básico concluído com sucesso!'))
        self.stdout.write(self.style.SUCCESS('O restante do setup (criação de unidades, etc.) acontecerá quando o jogador entrar na partida pelo lobby.'))

