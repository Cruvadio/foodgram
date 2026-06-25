from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Recipe(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    image = models.ImageField(
        upload_to='recipes/pictures/',
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления', validators=[MinValueValidator(1)]
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        blank=True,
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmountPerRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    published_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        unique_together = ('name', 'author')
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-published_date',)

    def __str__(self):
        return f'{self.name} {self.author.username} {self.cooking_time} '


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        verbose_name_plural = 'Тэги'
        verbose_name = 'Тэг'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=100,
        verbose_name='Единица измерения',
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
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество', validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = ('recipe', 'ingredient')
        verbose_name = 'Количество ингредиента на рецепт'
        verbose_name_plural = 'Количества ингредиента на рецепт'

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f' {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    class Meta:
        unique_together = ('recipe', 'user')
        verbose_name = 'Любимый'
        verbose_name_plural = 'Любимые'

    def __str__(self):
        return f'{self.user} - {self.recipe}'


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепт',
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user} - {self.recipe}'
