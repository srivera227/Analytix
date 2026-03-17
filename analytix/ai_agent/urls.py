from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # ejemplo
    path('', views.vistaHome, name='vistaHome'),
]