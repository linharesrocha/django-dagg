# Generated by Django 2.1.15 on 2023-05-04 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0017_metricasmercadolivre_ultima_atualizacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='metricasmercadolivre',
            name='vende_a_cada_visita',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
