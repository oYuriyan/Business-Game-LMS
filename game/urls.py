from django.urls import path
from game.views import login, dashboard, admin, landing, produtos # Importa as views separadas por módulo

urlpatterns = [

    # Login e logout
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),

    # Área do usuário
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
    path('lobby/', dashboard.lobby_view, name='lobby'),

    # Painel do administrador
    path('admin/', admin.admin_view, name='admin'),
    path('produtos/', produtos.listar_produtos, name='listar_produtos'),
    path('produtos/criar/', produtos.criar_produto, name='criar_produto'),
    path('produtos/editar/<int:produto_id>/', produtos.editar_produto, name='editar_produto'),
    path('produtos/excluir/<int:produto_id>/', produtos.excluir_produto, name='excluir_produto'),

    path('admin/rodada/<int:rodada_id>/definir_demanda/', admin.definir_demanda_rodada, name='definir_demanda_rodada'),

    #Home
    path('', landing.landing_page_view, name='home')
]