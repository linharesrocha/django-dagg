# Generated by Django 2.1.15 on 2023-07-05 11:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0024_auto_20230705_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedidoscompra',
            name='vlr_custo_novo',
        ),
    ]
