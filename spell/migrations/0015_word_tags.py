# Generated by Django 4.0.3 on 2022-06-27 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0014_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, to='spell.tag'),
        ),
    ]
