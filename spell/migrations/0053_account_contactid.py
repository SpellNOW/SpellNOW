# Generated by Django 4.0.3 on 2023-01-02 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0052_remove_account_contactid_remove_account_newsletter'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='contactid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
