import os
import sys
import pytest
from django.test import Client
from django.contrib.auth import get_user_model

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
        password=fake.password(),
        # first_name=fake.first_name(),
        # last_name=fake.last_name(),
    )


