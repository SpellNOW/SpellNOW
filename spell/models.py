from django.db import models
from django.forms import BooleanField
from django.contrib.auth.models import User
from django import forms

# Create your models here.
class Account(User):
    trigger = models.BooleanField()
    changenotifs = models.BooleanField()
    parent = models.BooleanField()
    children = models.ManyToManyField("Account", blank=True)
    parents = models.IntegerField(null=True, blank=True)
    repsub = models.BooleanField()
    contactid = models.IntegerField(null=True, blank=True)

class ConfirmReq(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    lock1 = models.IntegerField()
    lock2 = models.IntegerField()

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
    rooted = models.BooleanField()
    tags = models.ManyToManyField("Tag", blank=True)
    roots = models.ManyToManyField("Root", blank=True)

class Tag(models.Model):
    parent = models.ForeignKey("Tag", on_delete=models.CASCADE, null=True)
    name = models.TextField(max_length=100)

class Report(models.Model):
    used = models.TextField(max_length=100)
    correct = models.IntegerField()
    total = models.IntegerField()
    percent = models.FloatField()
    finished = models.DateTimeField(auto_now_add=True)
    specific = models.BooleanField()
    iid = models.IntegerField(null=True, blank=True)
    spelling = models.BooleanField()
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)

class SavedActivity(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    ids_used = models.TextField()
    correct_array = models.TextField()
    order = models.TextField()
    attempts = models.TextField()
    times = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    global_count = models.IntegerField()
    acc_count = models.IntegerField()
    correct = models.IntegerField()
    progress = models.IntegerField()
    total = models.IntegerField()
    words = models.TextField()
    speech = models.TextField()
    origin = models.TextField()
    definition = models.TextField()
    prons = models.TextField()
    final_tags = models.TextField()
    final_roots = models.TextField()

class SavedVocabActivity(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    ids_used = models.TextField()
    correct_array = models.TextField()
    order = models.TextField()
    attempts = models.TextField()
    times = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    global_count = models.IntegerField()
    acc_count = models.IntegerField()
    correct = models.IntegerField()
    progress = models.IntegerField()
    total = models.IntegerField()
    words = models.TextField()
    questions = models.TextField()
    options = models.TextField()
    answers = models.TextField()
    vocabas = models.TextField()

class ReportDetail(models.Model):
    count = models.IntegerField()
    identification = models.TextField(max_length=600)
    word = models.TextField(max_length=100)
    attempt = models.TextField()
    result = models.TextField(max_length=10)
    finished = models.DateTimeField(auto_now_add=True)
    time = models.TextField(max_length=600)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

class VocabReportDetail(models.Model):
    count = models.IntegerField()
    identification = models.TextField(max_length=600)
    question = models.TextField(max_length=1100)
    answer = models.TextField(max_length=1000)
    attempt = models.TextField(max_length=1000)
    result = models.TextField(max_length=10)
    finished = models.DateTimeField(auto_now_add=True)
    time = models.TextField(max_length=600)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

class Root(models.Model):
    name = models.TextField(max_length=100)
    definition = models.TextField(max_length=1000, null=True, blank=True)
    origin = models.TextField(max_length=1000, null=True, blank=True)
    pp = models.CharField(max_length=4, null=True, blank=True)

class EmailValidate(models.Model):
    userid = models.IntegerField()
    email = models.TextField(max_length=300)
    lock1 = models.IntegerField()
    lock2 = models.IntegerField()