from typing import Optional, Type

from django_filters.rest_framework import DjangoFilterBackend
from pyshorteners import Shortener
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from django.contrib.auth import get_user_model
from django.db.models import BooleanField, Exists, OuterRef, Value
from django.http import HttpResponse

from recipes.models import Cart, Ingredient, Recipe, Tag

from .filters import RecipesFilter
from .permissions import CurrentUser, IsAuthorOrReadOnly
from .serializers import (
    AvatarRequestSerializer,
    AvatarResponseSerializer,
    CartSerializer,
    FavoriteSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserFollowingsSerializer,
    UserProfileSerializer,
)
from .utils import make_ingredients_in_cart_list

User = get_user_model()


class SubscribeMixin:
    def _toggle(self, request, action_serializer_class):
        instance = self.get_object()
        serializer = action_serializer_class(
            data={}, context={'request': request, 'instance': instance}
        )
        serializer.is_valid(raise_exception=True)
        relation = serializer.get_relation()
        if request.method == 'POST':
            serializer.save(**relation)
            return Response(
                self.get_serializer(instance).data,
                status=status.HTTP_201_CREATED,
            )
        action_serializer_class.Meta.model.objects.filter(
            **relation
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = [
        'get',
    ]
    pagination_class = None


class MultiSerializerViewSetMixin:
    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()


class RecipeViewSet(ModelViewSet, SubscribeMixin, MultiSerializerViewSetMixin):
    permission_classes = [IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    serializer_class = RecipeSerializer
    serializer_classes = {
        'shopping_cart': ShortRecipeSerializer,
        'favorite': ShortRecipeSerializer,
    }

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Recipe.objects.select_related('author')
            .prefetch_related('tags', 'ingredients')
            .order_by('-published_date')
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    user.favorites.filter(recipe__id=OuterRef('pk'))
                ),
                is_in_shopping_cart=Exists(
                    Cart.objects.filter(user=user, recipe=OuterRef('pk'))
                ),
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField()),
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def short_link(self, request, pk=None):
        relative_url = f'/recipes/{pk}/'
        absolute_url = request.build_absolute_uri(relative_url)
        tiny_type = Shortener()
        shortened_url = tiny_type.tinyurl.short(absolute_url)
        return Response(
            {'short-link': shortened_url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self._toggle(request, FavoriteSerializer)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self._toggle(request, CartSerializer)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        shopping_list = make_ingredients_in_cart_list(request.user)
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class UserViewSet(
    mixins.RetrieveModelMixin,
    GenericViewSet,
    SubscribeMixin,
    MultiSerializerViewSetMixin,
):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all().prefetch_related('recipes')
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [AllowAny]
    serializer_classes = {
        'subscribe': UserFollowingsSerializer,
        'create': UserCreateSerializer,
        'avatar': AvatarRequestSerializer,
    }

    lookup_value_regex = '[0-9]+'

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.prefetch_related('recipes')
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    user.following.filter(following__id=OuterRef('pk'))
                ),
            )
        else:
            queryset = queryset.annotate(
                is_subscribed=Value(False, output_field=BooleanField()),
            )
        return queryset

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[CurrentUser],
    )
    def avatar(self, request):
        if request.method == 'PUT':
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            request.user.avatar = serializer.validated_data['avatar']
            request.user.save()
            data = AvatarResponseSerializer(instance=request.user).data
            return Response(data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
        serializer_class=UserFollowingsSerializer,
    )
    def subscribe(self, request, pk=None):
        return self._toggle(request, FollowSerializer)


class SubscriptionViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserFollowingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = User.objects.prefetch_related('recipes').filter(
            followers__follower=user
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_subscribed=Exists(
                    queryset.filter(following__id=OuterRef('pk'))
                ),
            )
        else:
            queryset = queryset.annotate(
                is_subscribed=Value(False, output_field=BooleanField()),
            )
        return queryset


class IngredientViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet
):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = [AllowAny]
    filter_backends = [
        SearchFilter,
    ]
    search_fields = [
        '^name',
    ]
