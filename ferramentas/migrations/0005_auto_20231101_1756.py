# Generated by Django 2.1.15 on 2023-11-01 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ferramentas', '0004_auto_20231101_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataultimobalanco',
            name='codid',
            field=models.IntegerField(),
        ),
    ]
