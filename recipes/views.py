from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import Recipe, MealLog, Ingredient
from .forms import RecipeForm
from django.forms import ModelForm
from django.contrib import messages

class IngredientForm(ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name']


@login_required
def add_ingredient(request):
    """
    Handles the creation of a new ingredient and stays on the same page.
    """
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Successfully added new ingredient: {form.cleaned_data['name']}")
            form = IngredientForm()  # Create a new, blank form
    else:
        form = IngredientForm()

    return render(request, 'recipes/add_ingredient.html', {'form': form})


@login_required
def add_recipe(request):
    """
    Handles the creation of a new recipe with a dual-listbox for ingredients.
    """
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.user = request.user
            recipe.save()
            form.save_m2m()
            return redirect('recipes:my_recipes')
    else:
        form = RecipeForm()

    # For a new recipe, all ingredients are available, and none are selected.
    available_ingredients = Ingredient.objects.all().order_by('name')
    selected_ingredients = Ingredient.objects.none()

    context = {
        'form': form,
        'available_ingredients': available_ingredients,
        'selected_ingredients': selected_ingredients,
    }
    return render(request, 'recipes/add_recipe.html', context)



@login_required
def my_recipes(request):
    """
    Shows a list of all recipes created by the current user.
    """
    recipes = Recipe.objects.filter(user=request.user)
    return render(request, 'recipes/my_recipes.html', {'recipes': recipes})


@login_required
def recipe_detail(request, pk):
    """
    Displays the full details of a specific recipe, including its cooking instructions,
    ingredients, and a log of dates it was chosen.
    """
    recipe = get_object_or_404(Recipe, pk=pk)
    meal_logs = MealLog.objects.filter(recipe=recipe).order_by('-chosen_date')
    context = {
        'recipe': recipe,
        'meal_logs': meal_logs,
        'ingredients': recipe.ingredients.all(),
    }
    return render(request, 'recipes/recipe_detail.html', context)


@login_required
def meal_suggestions(request):
    """
    Provides 3 meal suggestions, excluding any meals chosen in the last 30 days.
    If there are not enough qualifying meals, older ones are included.
    """
    thirty_days_ago = timezone.now().date() - timedelta(days=30)

    suggestions = list(Recipe.objects.filter(
        user=request.user
    ).filter(
        Q(last_chosen__lte=thirty_days_ago) | Q(last_chosen__isnull=True)
    ).order_by('?'))

    suggestions_for_display = suggestions[:3]

    return render(request, 'recipes/meal_suggestions.html', {'suggestions': suggestions_for_display})


@login_required
def choose_meal(request, pk):
    """
    Updates a meal's 'last_chosen' field and logs the choice in MealLog.
    """
    if request.method == 'POST':
        recipe = get_object_or_404(Recipe, pk=pk, user=request.user)
        recipe.last_chosen = timezone.now().date()
        recipe.save()
        MealLog.objects.create(recipe=recipe, user=request.user)
    return redirect('recipes:meal_suggestions')


@login_required
def edit_recipe(request, pk):
    """
    Handles the editing of an existing recipe's main details and ingredients.
    The ingredient management uses a client-side dual-listbox approach.
    """
    recipe = get_object_or_404(Recipe, pk=pk, user=request.user)

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipes:recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)

    available_ingredients = Ingredient.objects.exclude(recipes__in=[recipe]).order_by('name')
    selected_ingredients = recipe.ingredients.all().order_by('name')

    context = {
        'form': form,
        'recipe': recipe,
        'available_ingredients': available_ingredients,
        'selected_ingredients': selected_ingredients,
    }
    return render(request, 'recipes/edit_recipe.html', context)
