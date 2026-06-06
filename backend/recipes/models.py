from django.conf import settings
from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=100, help_text='Заголовок')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='Автор рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/pictures/', help_text='Картинка рецепта'
    )
    text = models.TextField(help_text='Описание рецепта')
    cooking_time = models.IntegerField(
        help_text='Время приготовления (минуты)'
    )
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', blank=True, help_text='Теги рецепта'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmountPerRecipe',
        related_name='recipes',
        help_text='Ингредиенты рецепта',
    )

    published_date = models.DateTimeField(
        help_text='Дата публикации рецепта', auto_now_add=True
    )

    class Meta:
        unique_together = ('name', 'author')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} {self.author.username} {self.cooking_time} '


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Название')
    slug = models.SlugField(unique=True, help_text='Слаг')

    class Meta:
        verbose_name_plural = 'Тэги'
        verbose_name = 'Тэг'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text='Название')
    measurement_unit = models.CharField(
        max_length=100, help_text='Единица измерения'
    )

    class Meta:
        verbose_name_plural = 'Ингредиенты'
        verbose_name = 'Ингредиент'

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class IngredientAmountPerRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amounts',
        help_text='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        help_text='Ингредиент',
    )
    amount = models.FloatField(help_text='Количество ингредиента')

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Количество ингредиента на рецепт'
        verbose_name_plural = 'Количества ингредиента на рецепт'

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f' {self.ingredient.measurement_unit}'
        )


# class IngredientAmountPerCart(models.Model):
#     cart = models.ForeignKey('Cart', on_delete=models.CASCADE, )
#     ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, )
#     amount = models.FloatField()
#
#     class Meta:
#         unique_together = ('cart', 'ingredient')
#         verbose_name = 'Количество ингредиента на рецепт'
#         verbose_name_plural = 'Количества ингредиента на рецепт'


class Cart(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        help_text='Хозяин корзины',
    )
    recipes = models.ManyToManyField(
        'Recipe', related_name='carts', help_text='Рецепты в корзине'
    )

    class Meta:
        verbose_name_plural = 'Корзины'
        verbose_name = 'Корзина'

    def __str__(self):
        return f'{self.owner.username} {self.recipes.count()}'
