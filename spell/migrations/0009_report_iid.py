# Generated by Django 4.0.3 on 2022-05-03 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0008_report_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='iid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
