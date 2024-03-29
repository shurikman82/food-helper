from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Recipe(models.Model):
    '''Модель рецепта.'''
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(upload_to='recipes/images',
                              verbose_name='Фотография рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1)],
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='Автор рецепта',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации рецепта',
        db_index=True,
    )
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', verbose_name='Теги рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredient', related_name='ingredients',
        through='RecipeIngredient', verbose_name='Ингредиенты рецепта',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    '''Модель тега.'''
    name = models.CharField(max_length=200, unique=True,
                            verbose_name='Название тега')
    color = models.CharField(max_length=7, unique=True,
                             null=True, verbose_name='Цвет тега')
    slug = models.SlugField(max_length=200, null=True,
                            unique=True, verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    '''Модель ингредиента.'''
    name = models.CharField(max_length=200,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name + ' ' + self.measurement_unit


class RecipeIngredient(models.Model):
    '''Модель ингредиета в конкретном рецепте.'''
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name} : {self.ingredient.name} {self.amount}'


class Favorite(models.Model):
    '''
    Модель избранных рецептов.
    '''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='favorite', verbose_name='Рецепт'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в избранное',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в избранное'


class ShoppingCart(models.Model):
    '''Модель корзины покупок.'''
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='shopping_cart', verbose_name='Рецепт в списке покупок'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в список покупок',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart_user_recipe',
            )
        ]

    def __str__(self):
        return f'{self.user} добавил {self.recipe} в список покупок'
