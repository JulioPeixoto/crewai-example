# example/views.py
from datetime import datetime
import base64

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.contrib import messages

import markdown2

from .models import Noticia
from .crewai.crew import NewsCrew
from .langchain import TitleGenerator


@cache_page(60 * 15)
def index(request):
    page_number = request.GET.get("page", 1)

    noticias_list = (
        Noticia.objects.all()
        .order_by("-data_publicacao")
        .only("titulo", "texto", "links", "imagem", "tipo_imagem", "data_publicacao")
    )

    paginator = Paginator(noticias_list, 10)
    noticias = paginator.get_page(page_number)

    for noticia in noticias:
        if noticia.imagem:
            imagem_base64 = base64.b64encode(noticia.imagem).decode("utf-8")
            noticia.imagem_base64 = f"data:{noticia.tipo_imagem};base64,{imagem_base64}"

    context = {
        "noticias": noticias,
        "page_obj": noticias,
    }
    return render(request, "index.html", context)


def gerar_noticias(request):
    if request.method == "POST":
        try:
            news_crew = NewsCrew()
            crew_results = news_crew.run()
            title_generator = TitleGenerator()

            for result in crew_results:
                content_lines = result.split("\n")
                content_without_title = "\n".join(content_lines[1:]) if content_lines else ""
                titulo = title_generator.create_title(content_without_title)
                html_content = markdown2.markdown(content_without_title)

                Noticia.objects.create(
                    titulo=titulo,
                    texto=html_content,
                    data_publicacao=timezone.now()
                )

            messages.success(request, "Notícias geradas com sucesso!")
        except Exception as e:
            print(e)
            messages.error(request, f"Erro ao gerar notícias: {str(e)}")

        return redirect("index")

    return redirect("index")
