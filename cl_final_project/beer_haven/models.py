# from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Recipe(models.Model):
    STATUS = (
        ('DT', 'Draft'),
        ('PD', 'Published'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField()
    prep_description = models.TextField()
    estimated_abv = models.FloatField(default=0, validators=[MinValueValidator(0.0), MaxValueValidator(40.0)])
    votes = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    published = models.DateTimeField(default=timezone.now)
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient', related_name='recipe_ing')
    categories = models.ManyToManyField('Category', related_name='recipe_cat')
    status = models.CharField(max_length=2, choices=STATUS)
    image = models.ImageField(upload_to='beer_haven/recipes_img/', blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published']


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=128)
    category = models.ForeignKey('Category', related_name='ingredient_cat', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='beer_haven/ingredients_img/', blank=True)
    description = models.TextField()
    in_stock = models.BooleanField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    amount = models.PositiveIntegerField()


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class ExperienceTip(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='tips', on_delete=models.CASCADE)
    content = models.TextField()
    published = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-published']


class Dictionary(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)
    content = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Dictionary'
        verbose_name_plural = 'Dictionaries'
