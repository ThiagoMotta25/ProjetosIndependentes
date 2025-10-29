from django.urls import path
from . import views

urlpatterns = [
    path("",views.login,name="login"),#Página inicial é a de login
    path("home/",views.home,name="home"),  
    path("sobre/",views.sobre,name="sobre"),
    path("musicas/",views.musicas,name="musicas"),
    
    path("login/",views.login,name="login"),
    path("logout/",views.logout,name="logout"),
    path("sign_up/",views.sign_up,name="sign_up"),

    path("perfil/",views.perfil,name="perfil"),
    path('foto_perfil/<int:usuario_id>/', views.foto_perfil, name='foto_perfil'),

    path("playlists/",views.playlists,name="playlists"),
    path("playlist/<int:id>/", views.playlist_detalhe, name="playlist_detalhe"),

]
