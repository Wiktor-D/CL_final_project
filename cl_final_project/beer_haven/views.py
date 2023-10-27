from django.shortcuts import render, redirect
from django.views import View

from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchVector
from django.views.generic import ListView, FormView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy

from .forms import LoginForm, SearchForm, UserRegistrationForm
from .models import Dictionary, Recipe, Ingredient, ExperienceTip


# Create your views here.
User = get_user_model()


class IndexView(View):
    def get(self, request):
        form = SearchForm()

        context = {
            'recent_recipes': Recipe.objects.all()[0:3],
            'form1': form,
        }
        return render(request, "beer_haven/index.html", context)

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Recipe.objects.annotate(
                search=SearchVector('title', 'description', 'prep_description', 'ingredients__name', 'categories__name'),
            ).filter(search=query).values('pk').distinct()
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
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class UserRegistrationView(CreateView):

    template_name = 'beer_haven/registration.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('user-list')


# @login_required
class UserDetails(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Renders User Detail View that requires login and handles user restriction"""

    model = User
    template_name = 'beer_haven/user-details.html'
    context_object_name = 'user'

    def test_func(self):
        """tests if url pk is the same as pk of logged user"""
        user_id = self.kwargs['pk']
        print(self.request.user.pk)
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
