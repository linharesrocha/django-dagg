# Generated by Django 2.1.15 on 2023-04-28 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercadolivre', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tokenmercadolivreapi',
            old_name='acess_token',
            new_name='access_token',
        ),
    ]