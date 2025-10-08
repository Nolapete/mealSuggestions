from django.contrib import admin
from .models import Recipe, MealLog, Ingredient

admin.site.register(Recipe)
admin.site.register(MealLog)
admin.site.register(Ingredient)
