
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
from django.core.mail import send_mail
import stripe

from decimal import Decimal
from stripe.error import StripeError
from .cart import Cart
from .forms import LoginForm, SearchForm, UserRegistrationForm, UserProfileForm, UserAddressForm, CartAddIngredientForm, GuestOrderCreateForm
from .models import Dictionary, Recipe, Ingredient, ExperienceTip, Profile, UserAddress, GuestOrderItem, GuestOrder
from cl_final_project.settings import EMAIL_HOST_USER, STRIPE_SECRET_KEY, STRIPE_API_VERSION


# Create your views here.
User = get_user_model()
stripe.api_key = STRIPE_SECRET_KEY
stripe.api_version = STRIPE_API_VERSION


class IndexView(View):
    def get(self, request):
        # form = SearchForm()

        context = {
            'recent_recipes': Recipe.objects.all().filter(status='PD')[:3],
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


# class UserRegistrationView(CreateView):
#
#     template_name = 'beer_haven/registration.html'
#     form_class = UserRegistrationForm
#     success_url = reverse_lazy('register')
#
#     def form_valid(self, form):
#         user = get_user_model()
#         new_user = user.objects.create_user(
#             first_name=form.cleaned_data['first_name'],
#             last_name=form.cleaned_data['last_name'],
#             username=form.cleaned_data['username'],
#             email=form.cleaned_data['email'],
#             password=form.cleaned_data['password']
#         )
#
#         Profile.objects.create(user=new_user)
#         # https://docs.djangoproject.com/en/4.2/ref/contrib/messages/
#         messages.success(self.request, 'Account created successfully')
#         return super().form_valid(form)

class UserRegistrationView(View):
    registration_form = UserRegistrationForm
    template_name = 'beer_haven/registration.html'

    def get(self, request):
        form = self.registration_form()
        return render(request, self.template_name, {'form': form})


    def post(self, request):
        form = self.registration_form(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(
                form.cleaned_data['password']
            )
            new_user.save()
            Profile.objects.create(user=new_user)
            messages.success(self.request, 'Account created successfully')

            return render(request, self.template_name, {})
        return render(request, self.template_name, {'form': form})


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
    paginate_by = 10

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

        """
    def post(self, request, ingredient_id):
        cart = Cart(request)
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        form = CartAddIngredientForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(
                ingredient=ingredient,
                amount=cd['amount'],
                override_amount=cd['override']
            )
        return redirect('cart_details')


@method_decorator(require_POST, name='dispatch')
class CartAddRecipeView(View):
    """ View to add all recipe ingredients to the shopping cart / update the amount of products already in it.
        The require_post decorator makes sure that only post requests are allowed.
        The view gets the ingredient_id parameter based on this id we retrieve the corresponding copy
        of the Ingredient model.
        If the form is valid we add the product to the cart and are redirected to the cart details page.

        """
    def post(self, request, recipe_id):
        cart = Cart(request)
        recipe = get_object_or_404(Recipe, id=recipe_id)
        cart.add_recipe(recipe)
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
        for item in cart:
            item['update_amount_form'] = CartAddIngredientForm(
                initial={
                    'amount': item['amount'],
                    'override': True
                }
            )
        return render(request, 'beer_haven/cart-details.html', {'cart': cart})




# class GuestOrderCreateView(CreateView):
#     template_name = 'beer_haven/order-create.html'
#     form_class = GuestOrderCreateForm
#     success_url = reverse_lazy('order_created')
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data()
#         cart = Cart(self.request)
#         context['cart'] = cart
#         return context
#
#     def form_valid(self, form):
#
#         guest_order = form.save()
#         cart = self.request.cart
#         for item in cart:
#             GuestOrderItem.objects.create(
#                 order=guest_order,
#                 ingredient=item['ingredient'],
#                 price=item['price'],
#                 amount=item['amount'],
#             )
#         cart.clear()
#
#         return super().form_valid(form)


class GuestOrderCreateView(View):
    """Guest order processing view.
    In the get method displays a form about the visitor's data and the contents
    of the shopping cart. In the post method, the shopping cart is saved to the
    database in the GuestOrderItem table, a notification email is sent, and the
    shopping cart is cleared. A redirection to the payment gateway follows. """

    guest_order_form = GuestOrderCreateForm
    template_name = 'beer_haven/order-create.html'

    def get(self, request):
        cart = Cart(request)
        form = self.guest_order_form()
        return render(request, self.template_name, {'form': form, 'cart': cart})

    def post(self, request):
        cart = Cart(request)
        form = self.guest_order_form(request.POST)
        if form.is_valid():
            guest_order = form.save()
            for item in cart:
                GuestOrderItem.objects.create(
                    order=guest_order,
                    ingredient=item['ingredient'],
                    price=item['price'],
                    amount=item['amount'],
                )
            self.send_order_email(guest_order, cart)
            cart.clear()
            request.session['order_id'] = guest_order.id


            return redirect(reverse('payment_process'))
            # return render(request, 'beer_haven/order-thx.html', {'order': guest_order})
        return render(request, self.template_name, {'form': form, 'cart': cart})

    def send_order_email(self, order, cart):
        subject = "order confirmation"
        message = f'Order (id: {order.id}) was successfully pledged. \n total cost: {order.get_total_cost()} \n Details: \n'
        for item in cart:
            message += f"{item['amount']} x {item['ingredient'].name} = {item['total_price']} \n"
        from_mail = EMAIL_HOST_USER
        recipient_mail = order.guest_email
        send_mail(subject, message, from_mail, [recipient_mail])


class PaymentProcess(View):
    """
    A view that supports the payment process. Get displays a template with an order
    summary and a button for payment. Clicking the button generates a POST request.
    A Stripe service checkout session is created with the most relevant parameters,
    success_url and cancel_url defined. Once the checkout session is created,
    a redirect to the Stripe service is returned.
    """
    def get(self, request):
        order_id = request.session.get('order_id', None)
        order = get_object_or_404(GuestOrder, id=order_id)
        print(order.id, order)

        return render(request, 'beer_haven/payment-process.html', {'order': order})


    def post(self, request):
        order_id = request.session.get('order_id', None)
        order = get_object_or_404(GuestOrder, id=order_id)
        # https://docs.djangoproject.com/en/4.2/ref/request-response/
        # https://stripe.com/docs/checkout/quickstart
        success_url = request.build_absolute_uri(reverse('payment_completed'))
        cancel_url = request.build_absolute_uri(reverse('payment_canceled'))
        # https://stripe.com/docs/api/checkout/sessions/object
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }

        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * 100),
                    'currency': 'pln',
                    'product_data': {
                        'name': item.ingredient.name,
                    },
                },
                'quantity': int(item.amount)
            })

        stripe_session = stripe.checkout.Session.create(**session_data)

        return redirect(stripe_session.url, code=303) # 303 code recommended to redirect web applications to a new URI after a POST request is made


class PaymentCompleted(View):
    def get(self, request):
        return render(request, 'beer_haven/payment-completed.html', {})


class PaymentCanceled(View):
    def get(self, request):
        return render(request, 'beer_haven/payment-canceled.html', {})

