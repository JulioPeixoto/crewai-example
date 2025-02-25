from django.db import models

class Noticia(models.Model):
    texto = models.TextField()

    class Meta:
        verbose_name = 'Notícia'
        verbose_name_plural = 'Notícias'

    def __str__(self):
        return self.texto 