# Generated by Django 5.0.4 on 2024-10-17 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0007_manager_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='failed_attempts',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='customer',
            name='is_locked',
            field=models.BooleanField(default=False),
        ),
        
    ]
