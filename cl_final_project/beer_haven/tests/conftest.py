import os
import sys
import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from .utils import create_fake_users, fake_tips, create_fake_ingredient, create_fake_recipe, dictionary_fake_posts
from beer_haven.models import Recipe, Ingredient, RecipeIngredient, Category

from faker import Faker


sys.path.append(os.path.dirname(__file__))
User = get_user_model()
fake = Faker()

@pytest.fixture
def client():
    client = Client()
    return client


@pytest.fixture
def random_user():
    """Create a sample User."""
    return User.objects.create_user(
        username=fake.user_name(),
        password='test',
        is_active=True,

    )

# @pytest.fixture
# def random_inactive_user():
#     """Create a sample User."""
#     return User.objects.create_user(
#         username=fake.user_name(),
#         password='test',
#         is_active=False,
#
#     )




@pytest.fixture
def recipe_set_up():
    for _ in range(10):
        Category.objects.create(
            name=fake.name(),
            slug=fake.slug()
        )
    for _ in range(10):
        create_fake_ingredient()
    for _ in range(5):
        create_fake_recipe()
    for _ in range(3):
        fake_tips()



@pytest.fixture
def dictionary_set_up():
    for _ in range(5):
        dictionary_fake_posts()


@pytest.fixture
def fake_users_group():
    for _ in range(5):
        create_fake_users()
