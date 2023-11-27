from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Recipe(models.Model):
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
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации рецепта')
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', verbose_name='Теги рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredient', related_name='ingredients',
        through='RecipeIngredient', verbose_name='Ингредиенты рецепта',
    )
    is_favorited = models.BooleanField(
        default=False, verbose_name='В избранном',
    )
    is_in_shopping_cart = models.BooleanField(
        default=False, verbose_name='В списке покупок',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):
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
    name = models.CharField(max_length=200, required=True,
                            verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200, required=True,
                                        verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name - self.measurement_unit


class RecipeIngredient(models.Model):
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


class Neo(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='neo', verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='neo', verbose_name='Рецепт'
    )
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата добавления в избранное')

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
