from django.db import models
from django.forms import BooleanField
from django.contrib.auth.models import User

# Create your models here.
class Account(User):
    pass

class Word(models.Model):
    word = models.TextField(max_length=100)
    speech = models.TextField(max_length=50)
    origin1 = models.TextField(max_length=600)
    origin2 = models.TextField(max_length=600)
    origin3 = models.TextField(max_length=600)
    definition1 = models.TextField(max_length=1000)
    definition2 = models.TextField(max_length=1000)
    definition3 = models.TextField(max_length=1000)
    pronounce = models.TextField(max_length=600)
    tagged = models.BooleanField()
    tags = models.ManyToManyField("Tag", null=True, blank=True)
    roots = models.ManyToManyField("Root", null=True, blank=True)

class Tag(models.Model):
    name = models.TextField(max_length=100)
    words = models.ManyToManyField(Word, null=True, blank=True)

class Report(models.Model):
    tags = models.TextField(max_length=100)
    correct = models.IntegerField()
    total = models.IntegerField()
    percent = models.FloatField()
    finished = models.DateTimeField(auto_now_add=True)
    specific = models.BooleanField()
    iid = models.IntegerField(null=True, blank=True)

class Root(models.Model):
    name = models.TextField(max_length=100)
    definition = models.TextField(max_length=1000, null=True, blank=True)
    origin = models.TextField(max_length=1000, null=True, blank=True)
    pp = models.CharField(max_length=4, null=True, blank=True)