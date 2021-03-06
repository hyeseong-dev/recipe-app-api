from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test1@testtest.com', password='testpass'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)
# 클래스 밖에서 함수를 생성해 둠으로써 클래스 안에서 호출시 메서드 호출만으로도 자유롭게 샘플 유저 객체생성이 가능

class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        '''Test creating a new user with an email is successful'''
        email = 'test@example.com'
        password = 'testpassword123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
    
    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@EXAMPLE.COM'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError): # value 에러를 발생시키지 않으면 테스트가 fail나요.
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@testtesttest.com',
            'test123'
        )
        self.assertTrue(user.is_superuser) # is_superuser 필드는 PermissionMixin클래스에 있는 변수명이에요.
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user=sample_user(), 
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)