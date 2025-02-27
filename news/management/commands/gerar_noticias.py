import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from news.crewai.noticias import Noticias
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Gera notícias automaticamente usando a classe Noticias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=1,
            help='Quantidade de notícias a serem geradas'
        )
        parser.add_argument(
            '--ignorar-erros',
            action='store_true',
            help='Continuar mesmo se houver erros de API'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        ignorar_erros = options['ignorar_erros']
        
        # Verificar se a chave da API está configurada
        serper_api_key = os.getenv('SERPER_API_KEY')
        if not serper_api_key:
            self.stdout.write(
                self.style.WARNING('AVISO: SERPER_API_KEY não está configurada. A geração de notícias pode falhar.')
            )
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando geração de {quantidade} notícia(s)...'))
        
        gerador = Noticias()
        
        # Corrigindo o método adicionar_noticia que está faltando
        if not hasattr(gerador, 'adicionar_noticia'):
            # Adicionando o método dinamicamente
            def adicionar_noticia(self, noticia):
                if noticia:
                    self.noticias.append(noticia)
            
            # Adicionando o método à instância
            setattr(Noticias, 'adicionar_noticia', adicionar_noticia)
        
        sucessos = 0
        falhas = 0
        
        for i in range(quantidade):
            try:
                self.stdout.write(f'Gerando notícia {i+1} de {quantidade}...')
                noticia = gerador.gerar_noticias()
                
                if noticia:
                    sucessos += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Notícia {i+1} gerada com sucesso! ID: {noticia.id}')
                    )
                else:
                    falhas += 1
                    self.stdout.write(
                        self.style.ERROR(f'Falha ao gerar notícia {i+1}')
                    )
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Operação interrompida pelo usuário.'))
                break
            except Exception as e:
                falhas += 1
                logger.error(f"Erro ao gerar notícia {i+1}: {str(e)}", exc_info=True)
                self.stdout.write(
                    self.style.ERROR(f'Erro ao gerar notícia {i+1}: {str(e)}')
                )
                if not ignorar_erros:
                    self.stdout.write(
                        self.style.WARNING('Interrompendo devido a erro. Use --ignorar-erros para continuar mesmo com erros.')
                    )
                    break
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Processo concluído. Sucessos: {sucessos}, Falhas: {falhas}'
            )
        ) 