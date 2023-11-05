import pytest

from random import sample, randint, choice
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from beer_haven.cart import Cart

from beer_haven.models import Recipe, Ingredient, ExperienceTip, Dictionary, Profile
from utils import fake_tips, create_fake_recipe, create_fake_ingredient, dictionary_fake_posts

User = get_user_model()

@pytest.mark.django_db
def test_landing_page(client, recipe_set_up):
    response = client.get(reverse('index'))
    assert response.status_code == 200
    recent_recipes = Recipe.objects.all().order_by('-created')[:3]
    context_recipes = response.context['recent_recipes']
    for recipe in context_recipes:
        assert recipe in recent_recipes


@pytest.mark.django_db
def test_login_page(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    client.login(username=random_user.username, password='test')
    assert response.status_code == 200

    response = client.get(reverse('user-details', kwargs={'pk': random_user.pk}))
    assert response.status_code == 200



@pytest.mark.django_db
def test_login_page_fail(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    client.force_login(random_user)
    response = client.get(reverse('user-details', kwargs={'pk': 7}))

    assert isinstance(response, HttpResponseForbidden)


@pytest.mark.django_db
def test_login_password_fail(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    response = client.post(reverse('login'), data={
        'username': random_user.username, 'password': 'incorrect_password'
    })
    assert 'Incorrect login or password!' in response.context['form'].errors['__all__']


@pytest.mark.django_db
def test_logout_page(client, random_user):
    response = client.get(reverse('login'))
    assert response.status_code == 200

    response = client.get(reverse('logout'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_user_registration(client, fake_users_group):
    client.logout()
    before_users = User.objects.count()
    user_data = {
        'first_name': 'Doktor',
        'last_name': 'Acula',
        'username': 'Dracula',
        'email': 'dracula@example.com',
        'password': 'foreveryoung',
    }

    response = client.post('/register/', user_data)
    assert response.status_code == 200
    assert response.context['form'].errors
    assert User.objects.count() == before_users + 1
    # new_user = User.objects.get(username='Dracula')
    # profile = Profile.objects.get(user=new_user)
    # assert profile.user == user
    #

@pytest.mark.django_db
def test_new_recipe(client, recipe_set_up):
    recipes_before = Recipe.objects.count()
    create_fake_recipe()
    assert Recipe.objects.count() == recipes_before + 1


@pytest.mark.django_db
def test_new_ingredient(client, recipe_set_up):
    ingredients_before = Ingredient.objects.count()
    create_fake_ingredient()
    assert Ingredient.objects.count() == ingredients_before + 1


@pytest.mark.django_db
def test_new_dictionary(client, dictionary_set_up):
    response = client.get(reverse('dictionary'))
    assert response.status_code == 200

    dictionary_posts = Dictionary.objects.count()
    dictionary_fake_posts()
    assert Dictionary.objects.count() == dictionary_posts + 1


@pytest.mark.django_db
def test_new_tip(client, recipe_set_up):
    tips_before = ExperienceTip.objects.count()
    fake_tips()
    assert ExperienceTip.objects.count() == tips_before + 1

    new_tip = ExperienceTip.objects.order_by('-published').first()
    recipe_id = new_tip.recipe.pk
    all_recipe_tips = ExperienceTip.objects.filter(recipe=new_tip.recipe)

    response = client.get(reverse('recipe-details', kwargs={'pk': recipe_id}))
    assert response.status_code == 200
    context_tips = response.context['experience_tips']
    for tip in context_tips:
        assert tip in all_recipe_tips


@pytest.mark.django_db
def test_recipe_list(client, recipe_set_up):
    response = client.get(reverse('recipes'))
    assert response.status_code == 200
    recipes = Recipe.objects.all()
    paginate_by = 10
    paginator = Paginator(recipes, paginate_by)

    if paginator.num_pages > 1:
        for page_num in range(1, paginator.num_pages + 1):
            response = client.get(reverse('recipes'), {'page': page_num})
            assert response.status_code == 200
            assert len(response.context['recipes']) <= paginate_by
    else:
        assert len(response.context['recipes']) <= paginate_by



@pytest.mark.django_db
def test_recipe_to_cart(client, recipe_set_up):
    recipes = Recipe.objects.all()
    recipe = choice(recipes)
    ingredients = recipe.ingredients.all()
    cart = Cart(client)
    response = client.post(reverse('cart_add_recipe', kwargs={'recipe_id': recipe.id}))
    assert response.status_code == 302


    for item in cart:
        assert item['ingredient'] in ingredients


@pytest.mark.django_db
def test_remove_from_cart(client, recipe_set_up):
    recipes = Recipe.objects.all()
    recipe = choice(recipes)
    ingredients = recipe.ingredients.all()
    ing = choice(ingredients)
    cart = Cart(client)
    response = client.post(reverse('cart_add_recipe', kwargs={'recipe_id': recipe.id}))
    assert response.status_code == 302

    response = client.post(reverse('cart_remove', kwargs={'ingredient_id': ing.id}))
    assert response.status_code == 302


@pytest.mark.django_db
def test_guest_order(client, recipe_set_up):
    recipes = Recipe.objects.all()
    recipe = choice(recipes)
    ingredients = recipe.ingredients.all()
    ing = choice(ingredients)
    cart = Cart(client)
    response = client.post(reverse('cart_add_recipe', kwargs={'recipe_id': recipe.id}))
    assert response.status_code == 302

    response = client.get(reverse('guest_order_create'))
    assert response.status_code == 200
    # guest_form_data = {
    #     'guest_first_name': 'name',
    #     'guest_last_name': 'surname',
    #     'guest_email': 'name@example.com',
    #     'guest_billing_address': 'address1',
    #     'guest_shipping_address': 'address2',
    #     'guest_postal_code': '33-333'
    # }
    response = client.post(reverse('guest_order_create'))
    assert response.status_code == 302





