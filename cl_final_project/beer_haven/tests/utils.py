from random import sample, randint, choice
from faker import Faker
from django.contrib.auth import get_user_model
from beer_haven.models import  ExperienceTip, Dictionary, Recipe, Ingredient, RecipeIngredient, Category

fake = Faker()
User = get_user_model()


def create_fake_ingredient():
    """Generate fake Ingredient data for setup"""
    category = Category.objects.all()
    Ingredient.objects.create(
        name=fake.name(),
        slug=fake.slug(),
        category=choice(category),
        description=fake.text(max_nb_chars=80),
        in_stock=True,
        price=19.84
    )


def create_fake_recipe():
    "Generate fake Recipe data for setup"
    ingredients = Ingredient.objects.all()
    categories = Category.objects.all()
    cat = choice(categories)
    ings = sample(list(ingredients), 4)
    new_recipe = Recipe.objects.create(
        title=fake.name(),
        slug=fake.slug(),
        description=fake.text(max_nb_chars=80),
        prep_description=fake.text(max_nb_chars=80),
        estimated_abv=5,
        status='PD'
    )
    for ing in ings:
        RecipeIngredient.objects.create(
            recipe=new_recipe,
            ingredient=ing,
            amount=42
        )


def dictionary_fake_posts():
    Dictionary.objects.create(
        title=fake.text(max_nb_chars=10),
        slug=fake.slug(),
        content=fake.text(max_nb_chars=80)
    )


def fake_tips():
    recipes = Recipe.objects.all()
    recipe = choice(recipes)
    ExperienceTip.objects.create(
        recipe=recipe,
        content=fake.text(max_nb_chars=80),
    )


def create_fake_users():
    """Create a sample User."""
    User.objects.create_user(
        username=fake.user_name(),
        password='test',
        is_active=True,
    )

