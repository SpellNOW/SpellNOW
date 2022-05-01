from django.db import models
from django.forms import BooleanField

# Create your models here.
class Word(models.Model):
    word = models.TextField(max_length=100)
    speech = models.TextField(max_length=50)
    origin = models.TextField(max_length=600)
    definition = models.TextField(max_length=1000)
    pronounce = models.TextField(max_length=600)
    tagged = models.BooleanField()

class Tag(models.Model):
    name = models.TextField(max_length=100)
    words = models.ManyToManyField(Word, null=True, blank=True)