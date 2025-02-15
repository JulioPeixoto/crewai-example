# example/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gerar-noticias/', views.gerar_noticias, name='gerar_noticias'),
]