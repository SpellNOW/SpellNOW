# Generated by Django 4.0.3 on 2022-04-15 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0004_tag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='words',
            field=models.ManyToManyField(blank=True, null=True, to='spell.word'),
        ),
    ]
