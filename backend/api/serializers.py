from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientAmountPerRecipe,
    Recipe,
    Tag,
)
from users.models import Follow

User = get_user_model()


class UserProfileSerializer(UserSerializer):
    avatar = serializers.ImageField(read_only=True, use_url=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'email',
        )
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.followers.filter(id=request.user.id).exists()


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'password': {'required': True, 'write_only': True},
            'username': {'required': True, 'write_only': False},
            'email': {'required': True, 'write_only': False},
            'first_name': {'required': True, 'write_only': False},
            'last_name': {'required': True, 'write_only': False},
        }


class AvatarRequestSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ('avatar',)
        model = User


class AvatarResponseSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True, use_url=True)

    class Meta:
        fields = ('avatar',)
        model = User


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            raise serializers.ValidationError(
                'Authentication credentials were not provided.'
            )
        user = request.user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError('Incorrect old password.')
        try:
            user.validate_password(data['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({'detail': e.messages}) from e
        user.validate_password(data['new_password'])
        user.set_password(data['new_password'])
        user.save()
        return data


class UserSignInSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True},
        }

    def validate(self, data):
        password1 = data.get('password')
        params = {
            'email': data.get('email'),
        }
        self.user = authenticate(
            request=self.context.get('request'), **params, password=password1
        )

        if not self.user:
            raise serializers.ValidationError(
                'Unable to log in with provided credentials.'
            )
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        extra_kwargs = {
            'slug': {'read_only': True},
            'name': {'read_only': True},
        }


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'measurement_unit': {'read_only': True},
            'name': {'read_only': True},
        }


class IngredientAmountPerRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True, source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmountPerRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError()
        return value


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountPerRecipeSerializer(
        source='ingredient_amounts', many=True, required=True
    )
    author = UserProfileSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    is_in_shopping_cart = serializers.BooleanField(read_only=True)
    is_favorited = serializers.BooleanField(read_only=True)
    image = Base64ImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'cooking_time',
            'image',
        )
        extra_kwargs = {
            'id': {'read_only': True},
            'name': {'required': True},
            'text': {'required': True},
            'cooking_time': {'required': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['tags'] = TagSerializer(
            instance.tags.all(), many=True
        ).data
        return representation

    def validate(self, attrs):
        ingredients = attrs.get('ingredient_amounts')
        tags = attrs.get('tags')
        if not tags:
            raise serializers.ValidationError('At least one tag is required.')
        if not ingredients:
            raise serializers.ValidationError(
                'At least one ingredient is required.'
            )
        return attrs

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Image is required.')
        return value

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'At least one ingredient is required.'
            )

        if len(value) != len({i.get('ingredient', None) for i in value}):
            raise serializers.ValidationError('Ingredients must be unique.')
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError('At least one tag is required.')
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Tags must be unique.')
        return value

    def add_ingredients_and_tags(self, ingredients, tags, instance):
        IngredientAmountPerRecipe.objects.bulk_create(
            IngredientAmountPerRecipe(recipe=instance, **ingredient)
            for ingredient in ingredients
        )
        instance.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredient_amounts', [])
        tags = validated_data.pop('tags', [])
        recipe = super().create(validated_data)
        self.add_ingredients_and_tags(ingredients, tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredient_amounts', [])
        tags = validated_data.pop('tags', [])
        instance.ingredient_amounts.all().delete()
        super().update(instance, validated_data)
        self.add_ingredients_and_tags(ingredients, tags, instance)
        return instance

    def validate_cooking_time(self, value):
        if value <= 0:
            raise serializers.ValidationError()
        return value

    def get_ingredients(self, obj):
        ingredient_amounts = obj.ingredient_amounts.select_related(
            'ingredient'
        ).all()
        return IngredientAmountPerRecipeSerializer(
            ingredient_amounts, many=True
        ).data


class UserFollowingsSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True, use_url=True)
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'email',
        )
        read_only_fields = ('id',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        query_params = request.query_params
        if query_params and query_params.get('recipes_limit', False):
            return ShortRecipeSerializer(
                obj.recipes.all()[: int(query_params['recipes_limit'])],
                many=True,
            ).data
        return ShortRecipeSerializer(
            obj.recipes.all()[: settings.DEFAULT_PAGE_SIZE], many=True
        ).data


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('recipes',)
        read_only_fields = ('recipes',)

    def validate(self, attrs):
        request = self.context['request']
        recipe = self.context.get('recipe')
        cart, _ = Cart.objects.get_or_create(owner=request.user)
        exists = cart.recipes.contains(recipe)
        if request.method == 'POST' and exists:
            raise serializers.ValidationError('Recipe already in cart.')
        elif request.method == 'DELETE' and not exists:
            raise serializers.ValidationError('Recipe not in cart.')

        self._cart = cart
        return attrs

    def save(self):
        recipe = self.context.get('recipe')
        if self.context['request'].method == 'POST':
            self._cart.recipes.add(recipe)
        else:
            self._cart.recipes.remove(recipe)
        return self._cart


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('recipe', 'user')
        read_only_fields = ('recipe', 'user')

    def validate(self, attrs):
        request = self.context['request']
        recipe = self.context['instance']
        exists = Favorite.objects.filter(
            recipe=recipe, user=request.user
        ).exists()
        if request.method == 'POST' and exists:
            raise serializers.ValidationError('Recipe already in favorites.')
        if request.method == 'DELETE' and not exists:
            raise serializers.ValidationError('Recipe not in favorites.')
        return attrs

    def save(self):
        request = self.context['request']
        recipe = self.context['instance']
        if request.method == 'POST':
            Favorite.objects.create(recipe=recipe, user=request.user)
        else:
            Favorite.objects.filter(recipe=recipe, user=request.user).delete()


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('follower', 'following')
        read_only_fields = ('follower', 'following')

    def validate(self, attrs):
        request = self.context['request']
        following = self.context['instance']
        if following == request.user:
            raise serializers.ValidationError('Cannot follow yourself.')
        exists = Follow.objects.filter(
            follower=request.user, following=following
        ).exists()
        if request.method == 'POST' and exists:
            raise serializers.ValidationError('Already following this user.')
        if request.method == 'DELETE' and not exists:
            raise serializers.ValidationError('Not following this user.')
        return attrs

    def save(self):
        request = self.context['request']
        following = self.context['instance']
        if request.method == 'POST':
            Follow.objects.create(follower=request.user, following=following)
        else:
            Follow.objects.filter(
                follower=request.user, following=following
            ).delete()
