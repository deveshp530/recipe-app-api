from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')

class PublicIngredientTest(TestCase):
    """Test publicly available ingredients api"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login ins required to retrieve tags"""
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsTests(TestCase):
    """Test private ingredients API"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test12@test.com',
            'testpass',
        )
        self.client.force_authenticate(self.user)   

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user(
            'new@test.com',
            'testpass'
        )
        Ingredient.objects.create(user=user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='Turmeric')

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_success(self):
        """Test creating new ingredient"""
        new_ingredient = {
            'name': 'Cabbage'
        }
        self.client.post(INGREDIENT_URL, new_ingredient)

        ingredient_exists = Ingredient.objects.filter(
            user=self.user,
            name=new_ingredient['name']
        ).exists()
        self.assertTrue(ingredient_exists)

    def test_create_ingredient_invalid(self):
        """Test creating new tag with invalid syntax"""
        new_ingredient = {
            'name': ''
        }
        res = self.client.post(INGREDIENT_URL, new_ingredient)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)