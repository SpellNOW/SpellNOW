# Generated by Django 4.0.3 on 2022-07-29 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0028_account_customer_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='customer_id',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
    ]
