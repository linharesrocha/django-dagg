# Generated by Django 2.1.15 on 2023-04-20 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0005_remove_posicaonetshoes_updated_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='posicaonetshoes',
            old_name='created_at',
            new_name='ultima_atualizacao',
        ),
    ]
