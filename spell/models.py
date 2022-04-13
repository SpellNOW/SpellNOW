from django.db import models

# Create your models here.
class Word(models.Model):
    word = models.TextField(max_length=100)
    speech = models.TextField(max_length=50)
    origin = models.TextField(max_length=600)
    definition = models.TextField(max_length=1000)
    pronounce = models.TextField(max_length=600)