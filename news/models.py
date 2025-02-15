from django.db import models

class Noticia(models.Model):
    titulo = models.TextField()
    texto = models.TextField()
    links = models.URLField(max_length=500, blank=True, null=True)
    imagem = models.BinaryField(blank=True, null=True)
    data_publicacao = models.DateTimeField(auto_now_add=True)
    nome_imagem = models.CharField(max_length=100, blank=True, null=True)
    tipo_imagem = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'
        ordering = ['-data_publicacao']

    def __str__(self):
        return self.titulo 