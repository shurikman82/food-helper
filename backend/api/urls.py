from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    #path('recipes/<int:pk>/favorite/', NeoViewset.as_view(), name='neo'),
    #path('recipes/<int:pk>/shopping_cart/', ShoppingCartViewset.as_view(), name='shopping_cart'),
    path('', include('djoser.urls')),
    path('', include(router.urls))
]
