# Generated by Django 4.2.6 on 2023-10-28 14:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beer_haven', '0006_recipeingredient_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
