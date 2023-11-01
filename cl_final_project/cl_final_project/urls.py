"""
URL configuration for cl_final_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from beer_haven import views as bh_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bh_views.IndexView.as_view(), name='index'),
    path('login/', bh_views.LoginView.as_view(), name='login'),
    path('logout/', bh_views.LogoutView.as_view(), name='logout'),
    path('register/', bh_views.UserRegistrationView.as_view(), name='register'),
    # AUTH VIEWS https://docs.djangoproject.com/en/4.2/topics/auth/default/
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('user-details/<int:pk>/', bh_views.UserDetails.as_view(), name='user-details'),
    path('dictionary/', bh_views.DictionaryView.as_view(), name='dictionary'),
    path('recipes/', bh_views.RecipesListView.as_view(), name='recipes'),
    path('recipe/<int:pk>/', bh_views.RecipeDetailsView.as_view(), name='recipe-details'),
    path('search/', bh_views.SearchView.as_view(), name='search'),
    path('edit-profile/', bh_views.EditProfile.as_view(), name='profile_change'),
    path('add-address/', bh_views.AddAddress.as_view(), name='add_address'),
    path('edit-address/<int:pk>/', bh_views.EditAddress.as_view(), name='address_change'),

    path('cart-add/<int:ingredient_id>/', bh_views.CartAddView.as_view(), name='cart_add'),
    path('cart-remove/<int:ingredient_id>/', bh_views.CartRemoveView.as_view(), name='cart_remove'),
    path('cart-details/', bh_views.CartDetailView.as_view(), name='cart_details'),
    path('cart-add-recipe/<int:recipe_id>/', bh_views.CartAddRecipeView.as_view(), name='cart_add_recipe'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# w środowisku produkcyjnym nie dostarczamy plików statycznych przy użyciu django