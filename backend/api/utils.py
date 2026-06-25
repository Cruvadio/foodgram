from .serializers import ShoppingCartIngredientsSerializer


def make_ingredients_in_cart_list(user):
    ingredients = ShoppingCartIngredientsSerializer(user).data['ingredients']
    shopping_list = 'Список покупок:\n\n'
    for item in ingredients:
        shopping_list += f'- {item["name"]}: {item["amount"]} {item["unit"]}\n'
    return shopping_list
