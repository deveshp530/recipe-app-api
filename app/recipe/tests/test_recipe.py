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





        


