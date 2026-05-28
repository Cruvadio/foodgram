from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe, Tag, Ingredient, Cart

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(read_only=True, use_url=True)
    is_subscribed = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'avatar',
                  'is_subscribed')
        read_only_fields = ('id',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.followers.filter(id=request.user.id).exists()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')
        extra_kwargs = {
            'password': {'required': True, 'write_only': True},
            'username': {'required': True, 'write_only': False},
            'email': {'required': True, 'write_only': False},
            'first_name': {'required': True, 'write_only': False},
            'last_name': {'required': True, 'write_only': False},
        }

class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)
    class Meta:
        fields = ('avatar',)
        model = User


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            raise serializers.ValidationError("Authentication credentials were not provided.")
        user = request.user
        if user.check_password(data['old_password']):
            try:
                user.validate_password(data['new_password'])
            except ValidationError as e:
                raise serializers.ValidationError({"detail": e.messages})
            user.validate_password(data['new_password'])
            user.set_password(data['new_password'])
            user.save()
            return data
        raise serializers.ValidationError("Incorrect old password.")

class UserSignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ('email', 'password')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        extra_kwargs = {
            'measurement_unit': {'read_only': True},
            'name': {'read_only': True},
        }

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favourite',
                  'is_in_shopping_cart', 'name', 'text', 'cooking_time')

    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.user_favourites.filter(id=request.user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Cart.objects.filter(owner_id=request.user.id,
                                   recipes=obj).exists()


