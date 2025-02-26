# Generated by Django 5.1.1 on 2025-02-15 21:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0078_delete_soldoutstatus'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoldOutStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_sold_out', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold_out_status', to='users.restaurantbranch')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sold_out_product', to='users.foodrawmaterial')),
            ],
        ),
    ]
