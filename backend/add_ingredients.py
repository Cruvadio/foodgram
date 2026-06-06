import json
import os
import sys

import django


def initialize_ingredients_list(path):
    from recipes.models import Ingredient

    with open(path, 'r', encoding='utf-8') as f:
        ingredients_list = json.load(f)

    ingredients = [Ingredient(**item) for item in ingredients_list]
    Ingredient.objects.bulk_create(ingredients)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    initialize_ingredients_list(sys.argv[1])
