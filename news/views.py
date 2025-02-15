# example/views.py
from datetime import datetime
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Noticia
import base64
from django.views.generic import ListView
from django.utils import timezone
from .crewai.crew import NewsCrew
import markdown2

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

class NoticiaListView(ListView):
    model = Noticia
    template_name = 'index.html'
    context_object_name = 'noticias'
    paginate_by = 10

    def get_queryset(self):
        # Executa o CrewAI para obter novas notícias
        news_crew = NewsCrew()
        crew_results = news_crew.run()

        # Processa os resultados usando o LangChain para títulos
        langchain_model = Model()
        titles = langchain_model.create_tittle(crew_results)

        # Converte os resultados em formato markdown para HTML
        for result in crew_results:
            # Assume que cada resultado está em formato markdown
            html_content = markdown2.markdown(result)
            
            # Extrai título, texto e data do markdown
            # (Isso depende do formato exato do seu markdown)
            titulo = titles  # Ou extraia do markdown se preferir
            texto = html_content
            data_publicacao = timezone.now()

            # Salva no banco de dados
            Noticia.objects.create(
                titulo=titulo,
                texto=texto,
                data_publicacao=data_publicacao
            )

        # Retorna todas as notícias ordenadas por data
        return Noticia.objects.all().order_by('-data_publicacao')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Converte o texto markdown para HTML antes de enviar para o template
        for noticia in context['noticias']:
            noticia.texto = markdown2.markdown(noticia.texto)
        return context