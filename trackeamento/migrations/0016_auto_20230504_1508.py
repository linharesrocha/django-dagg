# Generated by Django 2.1.15 on 2023-05-04 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0015_posicaomercadolivre'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PosicaoMercadoLivre',
            new_name='MetricasMercadoLivre',
        ),
    ]