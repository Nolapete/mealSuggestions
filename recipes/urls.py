from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('add/', views.add_recipe, name='add_recipe'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('suggestions/', views.meal_suggestions, name='meal_suggestions'),
    path('choose/<int:pk>/', views.choose_meal, name='choose_meal'),
    path('edit/<int:pk>/', views.edit_recipe, name='edit_recipe'),
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
]
