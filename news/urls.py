# example/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('noticias/', views.index, name='noticias'),
    path('gerar-noticias/', views.gerar_noticias, name='gerar_noticias'),
]