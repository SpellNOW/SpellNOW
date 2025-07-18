# Generated by Django 4.1.6 on 2023-06-24 08:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('spell', '0068_savedactivity_final_roots_savedactivity_final_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='SavedVocabActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ids_used', models.TextField()),
                ('correct_array', models.TextField()),
                ('order', models.TextField()),
                ('attempts', models.TextField()),
                ('times', models.TextField()),
                ('global_count', models.IntegerField()),
                ('acc_count', models.IntegerField()),
                ('correct', models.IntegerField()),
                ('progress', models.IntegerField()),
                ('total', models.IntegerField()),
                ('words', models.TextField()),
                ('questions', models.TextField()),
                ('options', models.TextField()),
                ('answers', models.TextField()),
                ('vocabas', models.TextField()),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spell.report')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='spell.account')),
            ],
        ),
    ]
