from django.urls import path
from game.views import login, dashboard

urlpatterns = [
    path('login/', login.login_view, name='login'),
    path('logout/', login.logout_view, name='logout'),
    path('dashboard/', dashboard.dashboard_view, name='dashboard'),
]