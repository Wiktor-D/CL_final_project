import pytest

from django.urls import reverse
from django.http import HttpResponseForbidden


@pytest.mark.django_db
def test_landing_page(client):
    response = client.get(reverse('index'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    client.login(username=random_user.username, password=random_user.password)
    print(random_user.username, random_user.password)

    response = client.get(reverse('user-details', kwargs={'pk': random_user.pk}))
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_page_fail(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    client.force_login(random_user)
    print(random_user.pk)
    response = client.get(reverse('user-details', kwargs={'pk': 7}))

    assert isinstance(response, HttpResponseForbidden)




