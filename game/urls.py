from django.urls import path
from game.views import login, dashboard, admin, landing # Importa as views separadas por módulo

urlpatterns = [

    # Login e logout
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),

    # Área do usuário
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
    path('lobby/', dashboard.lobby_view, name='lobby'),

    # Painel do administrador
    path('admin/', admin.admin_view, name='admin'),
    
    #Home
    path('', landing.landing_page_view, name='home')
]