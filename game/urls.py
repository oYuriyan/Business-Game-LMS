from django.urls import path
from game.views import login, dashboard
from game.views import lobby

urlpatterns = [
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
    path('lobby/', lobby.lobby_view, name='lobby'),
]
