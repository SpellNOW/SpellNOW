# Generated by Django 4.0.3 on 2023-01-02 20:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0051_account_contactid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='contactid',
        ),
        migrations.RemoveField(
            model_name='account',
            name='newsletter',
        ),
    ]
