# Generated by Django 5.0.7 on 2024-09-29 14:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0052_alter_inventory_quantity_alter_inventory_warehouse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='warehouse',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='inventories', to='users.warehouse'),
        ),
    ]
