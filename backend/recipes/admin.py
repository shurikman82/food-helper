from django.contrib import admin
from import_export.admin import ImportExportMixin

from .models import Ingredient, Recipe, Tag


class IngredientAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Ingredient, IngredientAdmin)
