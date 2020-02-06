from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='test@test.com',password='testpass'):
    return get_user_model().objects.create_user(email,password)

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating new user w/ email is successful"""
        email = 'test@test.com'
        password = 'test123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = 'test@test2.com'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())
        
    def test_new_user_invalid_email(self):
        """Test crating w/ no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test1234')

    def test_superuser_is_created(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@me.com',
            "test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_tag_str(self):
        """Test the tag string representiation"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )

        self.assertEqual(str(tag), tag.name)