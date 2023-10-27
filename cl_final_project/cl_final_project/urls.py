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
from beer_haven import views as bh_views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bh_views.IndexView.as_view(), name='index'),
    path('login/', bh_views.LoginView.as_view(), name='login'),
    path('logout/', bh_views.LogoutView.as_view(), name='logout'),
    path('register/', bh_views.UserRegistrationView.as_view(), name='register'),
    path('user-details/<int:pk>/', bh_views.UserDetails.as_view(), name='user-details'),
    path('dictionary/', bh_views.DictionaryView.as_view(), name='dictionary'),
    path('recipes/', bh_views.RecipesListView.as_view(), name='recipes'),
    path('recipe/<int:pk>/', bh_views.RecipeDetailsView.as_view(), name='recipe-details'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# w środowisku produkcyjnym nie dostarczamy plików statycznych przy użyciu django