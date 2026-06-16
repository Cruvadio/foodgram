from django.db.models import Sum

from api.serializers import CartSerializer


def make_ingredients_in_cart_list(request):
    serializer = CartSerializer(data={}, context={'request': request})
    serializer.is_valid(raise_exception=True)
    cart = serializer.save()
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
