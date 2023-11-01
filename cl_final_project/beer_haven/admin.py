from django.contrib import admin
from .models import Recipe, Ingredient, Category, ExperienceTip, Dictionary, RecipeIngredient, Profile, UserAddress
# Register your models here.




# https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'estimated_abv',
        'votes',
        'published',
        'status',
    )
    # fields connected to value of other fields
    prepopulated_fields = {"slug": ["title"]}
    # list of filters in the right filter bar
    list_filter = ['title', 'published', 'votes', 'status']
    date_hierarchy = 'published'
    inlines = [RecipeIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'category',
        'in_stock',
        'price'
    )

    prepopulated_fields = {"slug": ["name"]}
    list_filter = ['price', 'name', 'category']
    inlines = [RecipeIngredientInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )
    prepopulated_fields = {"slug": ["name"]}
    list_filter = ['name']


@admin.register(ExperienceTip)
class ExperienceTipAdmin(admin.ModelAdmin):
    list_display = [
        'recipe',
        'published'
    ]



@admin.register(Dictionary)
class DictionaryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
    ]
    prepopulated_fields = {"slug": ["title"]}
    list_filter = ['title']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birthdate', 'avatar']


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'street', 'building_nr', 'apartment_nr', 'postal_code', 'is_shipping_addr', 'is_billing_addr']

