# Generated by Django 2.1.15 on 2024-03-03 23:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0028_matchnetshoes'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchnetshoes',
            name='nome_loja',
            field=models.CharField(default=django.utils.timezone.now, max_length=255),
            preserve_default=False,
        ),
    ]
