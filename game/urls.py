# Em: game/urls.py

from django.urls import path
# Vamos organizar os imports das views para maior clareza
from game.views import login, dashboard, admin as admin_views, landing, produtos

urlpatterns = [
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),
    path('register/', login.register_view, name='register'), 
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
    path('lobby/', dashboard.lobby_view, name='lobby'),
    path('', landing.landing_page_view, name='home'),
    # URLs de Gerenciamento de Produtos
    path('produtos/', produtos.listar_produtos, name='listar_produtos'),
    path('produtos/criar/', produtos.criar_produto, name='criar_produto'),
    path('produtos/editar/<int:produto_id>/', produtos.editar_produto, name='editar_produto'),
    path('produtos/excluir/<int:produto_id>/', produtos.excluir_produto, name='excluir_produto'),
    path('estoque/<int:estoque_id>/reabastecer/', dashboard.reabastecer_estoque_view, name='reabastecer_estoque'),

    #URLs DO ADMIN
    path('admin/painel/', admin_views.painel_admin, name='painel_admin'),
    path('admin/partida/criar/', admin_views.criar_partida_view, name='criar_partida'),
    path('admin/partida/<int:partida_id>/avancar/', admin_views.avancar_rodada_view, name='avancar_rodada'),
    path('admin/rodada/<int:rodada_id>/demanda/', admin_views.definir_demanda_view, name='definir_demanda'),
    #URLs RODADA e PARTIDA
    path('partida/<int:partida_id>/entrar/', dashboard.entrar_partida_view, name='entrar_partida'),
    path('rodada/<int:rodada_id>/decidir/', dashboard.tomar_decisao_view, name='tomar_decisao'),
    path('rodada/<int:rodada_id>/resultados/', dashboard.resultados_rodada_view, name='resultados_rodada'),
]