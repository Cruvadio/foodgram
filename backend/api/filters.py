from django_filters import rest_framework as filters

from django.contrib.auth import get_user_model

from recipes.models import Recipe, Tag

User = get_user_model()


class RecipesFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='filter_favorite')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_favorite(self, queryset, name, value):
        user = self.request.user
        if not self.request.user.is_authenticated:
            return queryset
        if value == 1:
            return queryset.filter(favorited_by__user=user)
        else:
            return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        user = self.request.user
        if value == 1:
            return queryset.filter(carts__owner=user)
        return queryset
