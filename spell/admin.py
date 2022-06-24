from django.contrib import admin
from .models import Word, Tag, Report

admin.site.register(Word)
admin.site.register(Tag)
admin.site.register(Report)