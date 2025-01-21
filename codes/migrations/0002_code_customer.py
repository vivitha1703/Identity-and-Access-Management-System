# Generated by Django 5.0.4 on 2024-10-21 07:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0009_customuser_role'),
        ('codes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='code',
            name='customer',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='banking.customer'),
        ),
    ]
