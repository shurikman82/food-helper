from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import RecipeShortSerializer


class FavoriteAndShoppingCartActionsMixin:

    def favorite_and_shopping_cart_actions(self, request, pk, model):
        user = self.request.user
        recipe_objects = Recipe.objects.filter(id=pk).exists()
        if request.method == 'POST':
            if not recipe_objects:
                return Response({'errors': 'Рецепт не найден'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = Recipe.objects.get(id=pk)
            if model.objects.filter(recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(
                recipe, context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not recipe_objects:
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if not model.objects.filter(recipe=recipe_objects, user=user).exists():
            return Response({'errors': 'Рецепта для удаления нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(recipe=recipe_objects, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
