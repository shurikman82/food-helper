from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import RecipeShortSerializer


class FavoriteAndShoppingCartActionsMixin:

    def favorite_and_shopping_cart_actions(self, request, pk, model):
        user = self.request.user
        if request.method == 'POST':
            if not Recipe.objects.filter(id=pk).exists():
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
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        recipe = Recipe.objects.get(id=pk)
        if not model.objects.filter(recipe=recipe, user=user).exists():
            return Response({'errors': 'Рецепта для удаления нет'},
                            status=status.HTTP_400_BAD_REQUEST)
        model.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
