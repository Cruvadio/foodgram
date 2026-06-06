from django_filters.rest_framework import DjangoFilterBackend
from pyshorteners import Shortener
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from django.contrib.auth import get_user_model
from django.db.models import Sum

from recipes.models import Cart, Ingredient, Recipe, Tag

from .filters import RecipesFilter
from .permissions import CurrentUser, IsAuthorOrReadOnly
from .serializers import (
    AvatarRequestSerializer,
    AvatarResponseSerializer,
    IngredientSerializer,
    RecipeSerializer,
    ShortRecipeSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserFollowingsSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class SubscribeMixin:
    @staticmethod
    def subscribe_logic(self, request, queryset):
        instance = self.get_object()

        if request.method == 'POST':
            if queryset.filter(pk=request.user.pk).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            data = self.get_serializer(instance).data
            queryset.add(request.user)
            return Response(data=data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not queryset.filter(pk=request.user.pk).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            queryset.remove(request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    http_method_names = [
        'get',
    ]
    pagination_class = None


class RecipeViewSet(ModelViewSet, SubscribeMixin):
    queryset = (
        Recipe.objects.select_related('author')
        .all()
        .order_by('-published_date')
    )
    permission_classes = [IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action == 'shopping_cart' or self.action == 'favorite':
            return ShortRecipeSerializer
        else:
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        long_url = request.build_absolute_uri()
        tiny_type = Shortener()
        shortened_url = tiny_type.tinyurl.short(long_url)
        return Response(
            {'short-link': shortened_url}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.subscribe_logic(
            self, request, self.get_object().favourited_by
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        cart, _ = Cart.objects.get_or_create(owner=user)
        recipe = self.get_object()
        if request.method == 'POST':
            if cart.recipes.contains(recipe):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart.recipes.add(recipe)
            data = self.get_serializer(recipe).data
            return Response(data=data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not cart.recipes.contains(recipe):
                return Response(status=status.HTTP_400_BAD_REQUEST)
            cart.recipes.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        cart, _ = Cart.objects.get_or_create(owner=self.request.user)
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
        response = Response(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class UserViewSet(mixins.RetrieveModelMixin, GenericViewSet, SubscribeMixin):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all().prefetch_related('recipes')
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [AllowAny]

    lookup_value_regex = '[0-9]+'

    def get_serializer_class(self):
        if self.action == 'subscribe_toggle':
            return UserFollowingsSerializer
        if self.request.method == 'POST':
            return UserCreateSerializer
        if self.action == 'manage_avatar':
            return AvatarRequestSerializer
        else:
            return super().get_serializer_class()

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[CurrentUser],
    )
    def manage_avatar(self, request):
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
    def subscribe_toggle(self, request, pk=None):
        if self.get_object() == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return self.subscribe_logic(self, request, self.get_object().followers)


class SubscriptionViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = UserFollowingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(
            followers__id=self.request.user.id
        ).prefetch_related('recipes')


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
