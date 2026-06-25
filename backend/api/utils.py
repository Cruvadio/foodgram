from django.db.models import Sum

from recipes.models import Cart


def make_ingredients_in_cart_list(request):
    cart, _ = Cart.objects.get_or_create(owner=request.user)
    ingredients = (
        cart.recipes.values_list(
            'ingredient_amounts__ingredient__name',
            'ingredient_amounts__ingredient__measurement_unit',
        )
        .annotate(amount=Sum('ingredient_amounts__amount'))
        .order_by('ingredient_amounts__ingredient__name')
    )
    shopping_list = 'Список покупок:\n\n'
    for name, amount, unit in ingredients:
        shopping_list += f'- {name}: {amount} {unit}\n'
    return shopping_list
