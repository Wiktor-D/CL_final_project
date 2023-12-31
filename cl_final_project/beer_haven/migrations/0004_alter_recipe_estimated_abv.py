# Generated by Django 4.2.6 on 2023-10-22 12:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beer_haven', '0003_alter_category_options_alter_dictionary_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='estimated_abv',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(40.0)]),
        ),
    ]
