# example/views.py
import base64
import logging

# Imports de terceiros
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_page
import markdown2

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
        .order_by("-data_publicacao")
        .only("texto", "links", "imagem", "tipo_imagem", "data_publicacao")
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
    if request.method == "GET":
        try:
            data_atual = timezone.now()
            news_crew = NewsCrew(data=data_atual)
            crew_results = news_crew.run()            

            if not crew_results:
                raise ValueError("Nenhum resultado gerado pelos agentes")

            if hasattr(crew_results, 'raw_output'):
                content = crew_results.raw_output
            elif isinstance(crew_results, (list, tuple)):
                content = crew_results[0]
            else:
                content = str(crew_results)

            html_content = markdown2.markdown(content, extras=['fenced-code-blocks', 'tables'])
            
            try:
                noticia = Noticia.objects.create(
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

        return redirect("noticias")

    return redirect("noticias")
