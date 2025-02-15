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
            logger.info(f"Tipo do crew_results: {type(crew_results)}")
            logger.info(f"Conteúdo do crew_results: {crew_results}")
            
            title_generator = TitleGenerator()

            if not crew_results:
                logger.error("crew_results está vazio")
                raise ValueError("Nenhum resultado gerado pelos agentes")

            # Garantir que crew_results seja uma lista
            if isinstance(crew_results, (str, tuple)):
                crew_results = [crew_results]
            
            for i, result in enumerate(crew_results):
                logger.info(f"Processando resultado {i+1}")
                logger.info(f"Tipo do resultado: {type(result)}")
                
                # Se o resultado for uma tupla, pegar o primeiro elemento
                if isinstance(result, tuple):
                    result = result[0]
                
                logger.info(f"Conteúdo do resultado: {result[:200]}...")
                
                content_lines = result.split("\n")
                content_without_title = "\n".join(content_lines[1:]) if content_lines else ""
                
                titulo = title_generator.create_title(content_without_title)
                logger.info(f"Título gerado: {titulo}")
                
                html_content = markdown2.markdown(content_without_title)
                logger.info(f"HTML gerado: {html_content[:200]}...")

                try:
                    noticia = Noticia.objects.create(
                        titulo=titulo,
                        texto=html_content,
                        data_publicacao=timezone.now()
                    )
                    logger.info(f"Notícia salva com sucesso. ID: {noticia.id}")
                except Exception as db_error:
                    logger.error(f"Erro ao salvar no banco: {str(db_error)}")
                    logger.error(f"Dados da tentativa - Título: {titulo}, Texto: {html_content}")
                    raise

            messages.success(request, "Notícias geradas com sucesso!")
        except Exception as e:
            logger.error(f"Erro geral: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao gerar notícias: {str(e)}")

        return redirect("index")

    return redirect("index")
