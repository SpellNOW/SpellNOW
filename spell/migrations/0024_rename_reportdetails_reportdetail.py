# Generated by Django 4.0.3 on 2022-07-27 07:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0023_reportdetails_report_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReportDetails',
            new_name='ReportDetail',
        ),
    ]
