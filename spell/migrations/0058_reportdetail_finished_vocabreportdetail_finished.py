# Generated by Django 4.1.6 on 2023-06-22 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0057_savedactivity'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportdetail',
            name='finished',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='vocabreportdetail',
            name='finished',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
