from rest_framework import routers

from django.urls import include, path

from .views import (
    IngredientViewSet, RecipeViewSet, SubscriptionViewSet, TagViewSet,
    UserViewSet,
)

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')

router.register(r'tags', TagViewSet, basename='tags')
router.register(
    r'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
router.register(r'ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
