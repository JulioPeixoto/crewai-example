from django.db import models
from django.utils import timezone

class Noticia(models.Model):
    texto = models.TextField()
    data_publicacao = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'

    def __str__(self):
        return self.texto 