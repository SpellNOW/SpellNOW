from django.contrib import admin
from .models import Account, Word, Tag, Report

admin.site.register(Account)
admin.site.register(Word)
admin.site.register(Tag)
admin.site.register(Report)