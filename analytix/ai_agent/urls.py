from django.contrib import admin
from django.urls import path, include
from . import views
from modeler import views as apiModeler

urlpatterns = [
    # ejemplo
    path('', views.vistaHome, name='vistaHome'),
    path('synergy/apiBiAgent/', views.ai_query, name="ai_query"), 
    path("synergy/conectarDataBase/",apiModeler.conectar_bd,name="conectar_bd"),
    path("synergy/listarDataBase/",apiModeler.listarConexiones,name="listar_bd"),
    path("synergy/controller_cnx/",apiModeler.gestionarConexion,name="controller_cnx"),
]