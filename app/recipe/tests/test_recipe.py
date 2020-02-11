from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import *
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

# /api/recipe/recipes
# /api/recipe/recipes/1/

def detail_url(recipe_id):
    """return recipe detail url"""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def sample_tag(user, name='Main Course'):
    """Create and return sample tag"""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """Create and return sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user,**params):
    """Create and return sample recipe"""

    test_recipe = {
        'title': 'Mushroom Chicken',
        'time_minutes': 10,
        'price': 5.00
    }
    # update will create/update keys in dictionary
    test_recipe.update(params)

    return Recipe.objects.create(user=user, **test_recipe)

class PublicRecipeTests(TestCase):
    """Test publicly avaialble tags API"""
    def setup(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
  

class PrivateTagsTests(TestCase):
    """Test the unauthenticated recipe API"""
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test12@test.com',
            'testpass',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipe(self):
        """Test retrieving a list of recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited(self):
        """Test that recipes are retrieved for user"""

        user2 = get_user_model().objects.create_user(
            'new@test.com',
            'testpass'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """TEst viewing recipe detail"""  
        recipe=sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        new_recipe = {
            'title': 'Cake',
            'time_minutes': 30,
            'price': 15.00
        }

        res = self.client.post(RECIPE_URL, new_recipe)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in new_recipe.keys():
            self.assertEqual(new_recipe[key], getattr(recipe, key))
    
    def test_create_recipe_with_tags(self):
        """Creating recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')

        new_recipe = {
            'title': 'CheeseCake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 30,
            'price': 15.00   
        }
        res = self.client.post(RECIPE_URL, new_recipe)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Shrimp')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')

        new_recipe = {
            'title': 'Prawn curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 25,
            'price': 20.00   
        }
        res = self.client.post(RECIPE_URL, new_recipe)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)















        


