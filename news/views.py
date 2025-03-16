# example/views.py
import base64
import logging

# Imports de terceiros
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_page

# Imports locais
from .models import Noticia
from .crewai.crew import NewsCrew

logger = logging.getLogger(__name__)

def landing_page(request):
    return render(request, "landing_page.html")

@cache_page(60 * 15)
def index(request):
    page_number = request.GET.get("page", 1)

    noticias_list = (
        Noticia.objects.all()
    )

    paginator = Paginator(noticias_list, 10)
    noticias = paginator.get_page(page_number)

    return render(request, "index.html", {
        "noticias": noticias,
        "page_obj": noticias,
    })
