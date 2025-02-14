# example/views.py
from datetime import datetime
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Noticia
import base64

@cache_page(60 * 15)  
def index(request):
    page_number = request.GET.get('page', 1)
    
    noticias_list = Noticia.objects.all().order_by('-data_publicacao').only(
        'titulo', 'texto', 'links', 'imagem', 'tipo_imagem', 'data_publicacao'
    )
    
    paginator = Paginator(noticias_list, 10)
    noticias = paginator.get_page(page_number)
    
    for noticia in noticias:
        if noticia.imagem:
            imagem_base64 = base64.b64encode(noticia.imagem).decode('utf-8')
            noticia.imagem_base64 = f"data:{noticia.tipo_imagem};base64,{imagem_base64}"
    
    context = {
        'noticias': noticias,
        'page_obj': noticias,
    }
    return render(request, 'index.html', context)