# Generated by Django 2.1.15 on 2023-11-01 17:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ferramentas', '0003_dataultimobalanco'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataultimobalanco',
            name='cod_interno',
        ),
        migrations.AddField(
            model_name='dataultimobalanco',
            name='codid',
            field=models.CharField(default=django.utils.timezone.now, max_length=50),
            preserve_default=False,
        ),
    ]
