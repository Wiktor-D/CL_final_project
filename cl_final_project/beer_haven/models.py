# from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

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
    UNIT = (
        (0, "g"),
        (1, "kg"),
        (2, "piece"),
    )

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='ingredient_recipes')
    amount = models.FloatField(
        validators=[MinValueValidator(0)]
    )
    unit = models.PositiveSmallIntegerField(choices=UNIT, default=0)


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


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    birthdate = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='beer_haven/user_profile/', blank=True)


    def __str__(self):
        return self.user.username


class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    building_nr = models.PositiveSmallIntegerField(blank=True, null=True)
    apartment_nr = models.PositiveSmallIntegerField(blank=True, null=True)
    postal_code = models.CharField(max_length=6, blank=True, null=True)
    is_shipping_addr = models.BooleanField(default=False)
    is_billing_addr = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.city}, {self.street} bldg. {self.building_nr} apt. {self.apartment_nr}'

    class Meta:

        verbose_name = 'User address'
        verbose_name_plural = 'User addresses'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_user')
    billing_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='order_billing_addr')
    shipping_address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='order_shipping_addr')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)