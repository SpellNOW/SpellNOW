# Generated by Django 4.0.3 on 2022-08-01 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0029_alter_account_customer_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailValidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('userid', models.IntegerField()),
                ('email', models.TextField(max_length=300)),
                ('lock1', models.IntegerField()),
                ('lock2', models.IntegerField()),
            ],
        ),
    ]
