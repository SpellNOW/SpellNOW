from django.contrib import admin
from .models import Account, Word, Tag, Root, Report, ReportDetail, EmailValidate

admin.site.register(Account)
admin.site.register(Word)
admin.site.register(Tag)
admin.site.register(Root)
admin.site.register(Report)
admin.site.register(ReportDetail)
admin.site.register(EmailValidate)