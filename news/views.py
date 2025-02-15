# example/views.py
from datetime import datetime
import base64
import logging

from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.contrib import messages

import markdown2

from .models import Noticia
from .crewai.crew import NewsCrew
from .langchain import TitleGenerator

logger = logging.getLogger(__name__)

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

    return render(request, "index.html", {
        "noticias": noticias,
        "page_obj": noticias,
    })


def gerar_noticias(request):
    if request.method == "POST":
        try:
            news_crew = NewsCrew()
            crew_results = news_crew.run()            
            title_generator = TitleGenerator()

            if not crew_results:
                raise ValueError("Nenhum resultado gerado pelos agentes")

            if isinstance(crew_results, (str, tuple)):
                crew_results = [crew_results]
            
            for result in crew_results:
                if isinstance(result, tuple):
                    result = result[0]
                
                content_lines = result.split("\n")
                content_without_title = "\n".join(content_lines[1:]) if content_lines else ""
                
                titulo_response = title_generator.create_title(content_without_title)
                titulo = titulo_response.content if hasattr(titulo_response, 'content') else str(titulo_response)
                html_content = markdown2.markdown(content_without_title)

                try:
                    noticia = Noticia.objects.create(
                        titulo=titulo,
                        texto=html_content,
                        data_publicacao=timezone.now()
                    )
                    logger.info(f"Notícia salva com ID: {noticia.id}")
                except Exception as db_error:
                    logger.error(f"Erro ao salvar no banco: {str(db_error)}")
                    raise

            messages.success(request, "Notícias geradas com sucesso!")
        except Exception as e:
            logger.error(f"Erro: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao gerar notícias: {str(e)}")

        return redirect("index")

    return redirect("index")
