from .models import Ingredient
from decimal import Decimal


class Cart:
    def __init__(self, request):
        """ Cart initialization via self.session will allow access for other methods of the Cart class.
        We retrieve the shopping cart from the current session or create a new one when there is no existing
        one in the session."""
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, ingredient, amount=1, override_amount=False):
        """A method that allows to add a product to cart or change the quantity of that product.
        The dictionary uses the identifier of the ingredient as the key,
        and the quantity of the product and its price as the value.

        ingredient.id is converted to a text string because Django uses
        JSON format for serialized session data. Decimal is also converted for the same reason"""
        ingredient_id = str(ingredient.id)
        if ingredient_id not in self.cart:
            self.cart[ingredient_id] = {
                'amount': 0,
                'price': str(ingredient.price)
            }
        if override_amount:
            self.cart[ingredient_id]['amount'] = amount
        else:
            self.cart[ingredient_id]['amount'] += amount
        self.save()

    def save(self):
        """marking the session as modified, which will indicate, that it has been saved"""
        # https://docs.djangoproject.com/en/4.2/topics/http/sessions/
        self.session.modified = True

    def remove(self, ingredient):
        """ method removes the product from the cart dictionary based on the key (ingredient_id)
            and calls the save method to update the cart in the session """
        ingredient_id = str(ingredient.id)
        if ingredient_id in self.cart:
            del self.cart[ingredient_id]
            self.save()

    def __iter__(self):
        """ method allows you to iterate through the products in the cart
            and access the associated Ingredients model instances.
            1.  Ingredient IDs (keys) are retrieved from the shopping cart
            2.  Ingredient objects whose IDs are in the cart are retrieved.
            3.  A copy of the shopping cart is created to avoid changing the original cart.
            4.  In a "for" loop for each ingredient in the cart,
                information about the corresponding Ingredient object is added
                to the item in the cart, and price and total price calculations are performed.
            5.  Finally, the items in the cart are returned during the iteration."""
        ingredient_ids = self.cart.keys()
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        cart = self.cart.copy()
        for ingredient in ingredients:
            cart[str(ingredient.id)]['ingredient'] = ingredient
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['amount'] = Decimal(item['amount'])
            item['total_price'] = item['price'] * item['amount']
            yield item

    def get_total_price(self):
        """ method returns the total sum of the prices of all products in the shopping cart """
        costs = [Decimal(item['price']) * Decimal(item['amount']) for item in self.cart.values()]
        return sum(costs)

    def clear(self):
        """ method removes the contents of the cart"""
        del self.session['cart']
        self.save()

    def add_recipe(self, recipe):
        """ method adds to cart all ingredients in given recipe"""
        for ingredient in recipe.recipe_ingredients.all():
            self.add(ingredient.ingredient, ingredient.amount)

        session_data = dict(self.session.items())
        print(session_data)

