# Generated by Django 2.1.15 on 2023-06-28 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackeamento', '0019_auto_20230510_1412'),
    ]

    operations = [
        migrations.CreateModel(
            name='MetricasAds',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('desde', models.DateField()),
                ('ate', models.DateField()),
                ('nome_campanha', models.CharField(max_length=255)),
                ('acos_campanha', models.FloatField(blank=True, null=True)),
                ('mlb_anuncio', models.CharField(max_length=255)),
                ('titulo_anuncio', models.CharField(max_length=255)),
                ('preco_anuncio', models.FloatField(blank=True, null=True)),
                ('link_anuncio', models.CharField(max_length=255)),
                ('clicks_anuncio', models.IntegerField(blank=True, null=True)),
                ('impressions_anuncio', models.IntegerField(blank=True, null=True)),
                ('cost_anuncio', models.FloatField(blank=True, null=True)),
                ('cpc_anuncio', models.FloatField(blank=True, null=True)),
                ('ctr_anuncio', models.FloatField(blank=True, null=True)),
                ('cvr_anuncio', models.FloatField(blank=True, null=True)),
                ('sold_quantity_total_anuncio', models.IntegerField(blank=True, null=True)),
                ('amount_total_anuncio', models.FloatField(blank=True, null=True)),
                ('advertising_fee_anuncio', models.FloatField(blank=True, null=True)),
                ('organic_orders_quantity_anuncio', models.IntegerField(blank=True, null=True)),
                ('share_anuncio', models.FloatField(blank=True, null=True)),
            ],
        ),
    ]