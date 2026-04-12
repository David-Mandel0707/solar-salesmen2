from django.urls import path 
from. import views



urlpatterns=[
    path('', views.login, name="login"),
    path('cadastro/', views.cadastro, name="cadastro"),
    path('diretoria/', views.diretoria, name="diretoria"),
    path('pagina-Inicial/', views.paginaInicial, name="paginaInicial"),
    path('tornar-admin/', views.tornar_admin, name='tornar_admin')
]
