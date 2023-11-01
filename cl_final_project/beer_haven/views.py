from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector
from django.contrib import messages
from django.views.generic import ListView, FormView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy, reverse

from .cart import Cart
from .forms import LoginForm, SearchForm, UserRegistrationForm, UserProfileForm, UserAddressForm, CartAddRecipeForm
from .models import Dictionary, Recipe, Ingredient, ExperienceTip, Profile, UserAddress


# Create your views here.
User = get_user_model()


class IndexView(View):
    def get(self, request):
        # form = SearchForm()

        context = {
            'recent_recipes': Recipe.objects.all()[0:3],
            # 'form': form,
        }
        return render(request, "beer_haven/index.html", context)


class SearchView(View):
    def get(self, request):
        form = SearchForm()
        return render(request, "beer_haven/search.html", {'form': form})

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Recipe.objects.annotate(
                search=SearchVector('title', 'description', 'prep_description', 'ingredients__name', 'categories__name'),
            ).filter(search__icontains=query).values('pk').distinct()
            # getting ids
            recipe_ids = [result['pk'] for result in results]

            # finding full objects
            unique_results = Recipe.objects.filter(pk__in=recipe_ids)

            context = {

                'form': form,
                'query': query,
                'results': unique_results
            }
            return render(request, "beer_haven/search.html", context)
        return render(request, "beer_haven/search.html", {'form': form})


class LoginView(FormView):
    template_name = 'beer_haven/login.html'
    form_class = LoginForm
    # success_url = reverse_lazy('user-details')

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)

    def get_success_url(self):
        user_id = self.request.user.pk
        success_url = reverse('user-details', kwargs={'pk': user_id})
        return success_url


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class UserRegistrationView(CreateView):

    template_name = 'beer_haven/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register')

    def form_valid(self, form):
        user = get_user_model()
        new_user = user.objects.create_user(
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )

        Profile.objects.create(user=new_user)

        messages.success(self.request, 'Account created successfully')
        return super().form_valid(form)




class UserDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Renders User Detail View that requires login and handles user restriction"""

    model = User
    template_name = 'beer_haven/user-details.html'
    context_object_name = 'user'

    def test_func(self):
        """tests if url pk is the same as pk of logged user"""
        user_id = self.kwargs['pk']
        return self.request.user.id == user_id


class DictionaryView(ListView):
    """Renders Dictionary Page using generic ListView"""
    template_name = 'beer_haven/dictionary.html'
    model = Dictionary
    context_object_name = 'entries'


class RecipesListView(ListView):
    """Renders Recipes List View using generic ListView"""
    template_name = "beer_haven/recipes-list.html"
    model = Recipe
    context_object_name = 'recipes'
    paginate_by = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='PD')


class RecipeDetailsView(DetailView):
    model = Recipe
    template_name = 'beer_haven/recipe-details.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        experience_tips = ExperienceTip.objects.filter(recipe=context['recipe'])
        context['experience_tips'] = experience_tips
        if self.request.user.is_authenticated and self.request.user.is_staff:
            context['admin_or_superuser'] = True
        else:
            context['admin_or_superuser'] = False

        return context


class EditProfile(LoginRequiredMixin, FormView):
    template_name = 'beer_haven/profile-edit.html'
    form_class = UserProfileForm

    def get_success_url(self):
        user_id = self.request.user.pk
        success_url = reverse('user-details', kwargs={'pk': user_id})
        return success_url


class AddAddress(LoginRequiredMixin, CreateView):
    template_name = 'beer_haven/add-address.html'
    form_class = UserAddressForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        user_id = self.request.user.pk
        success_url = reverse('user-details', kwargs={'pk': user_id})
        return success_url


class EditAddress(LoginRequiredMixin, UpdateView):
    template_name = 'beer_haven/add-address.html'
    form_class = UserAddressForm
    model = UserAddress

    def get_success_url(self):
        user_id = self.request.user.pk
        success_url = reverse('user-details', kwargs={'pk': user_id})
        return success_url


# https://docs.djangoproject.com/en/4.2/topics/class-based-views/intro/
# transforms function decorator into a method decorator
@method_decorator(require_POST, name='dispatch')
class CartAddView(View):
    """ View to add products to the shopping cart / update the amount of products already in it.
        The require_post decorator makes sure that only post requests are allowed.
        The view gets the ingredient_id parameter based on this id we retrieve the corresponding copy
        of the Ingredient model.
        If the form is valid we add the product to the cart and are redirected to the cart details page.

        Args:
            param1 (int): ingredient_id

        Returns:
            Redirect to cart_detail

        """
    def post(self, request, ingredient_id):
        cart = Cart(request)
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        form = CartAddRecipeForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                ingredient=ingredient,
                amount=cd['amount'],
                override_amount=cd['override']
            )
        return redirect('cart_details')


@method_decorator(require_POST, name='dispatch')
class CartRemoveView(View):
    """ The view gets the ingredient_id parameter, based on this id it retrieves the corresponding instance
        of the Ingredient model and this ingredient is removed from the shopping cart. After that it redirects to the cart_detail url. """
    def post(self, request, ingredient_id):
        cart = Cart(request)
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        cart.remove(ingredient)
        return redirect('cart_details')


class CartDetailView(View):
    """view retrieves the current shopping cart and displays its contents """
    def get(self, request):
        cart = Cart(request)
        return render(request, 'beer_haven/cart-details.html', {'cart': cart})





