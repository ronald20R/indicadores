# Generated by Django 5.2.1 on 2025-06-04 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('modelos', '0008_tramitesmensual'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tramitesmensual',
            name='fecha_conclusion',
        ),
        migrations.RemoveField(
            model_name='tramitesmensual',
            name='fecha_ingreso',
        ),
    ]
