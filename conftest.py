"""
Pytest configuration and shared fixtures for Sports Game Tracker tests.
"""

import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Enable database access for all tests automatically.
    """
    pass


@pytest.fixture
def api_client():
    """
    Create an API client for testing REST API endpoints.
    """
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, django_user_model):
    """
    Create an authenticated API client with a test user.
    """
    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def test_user(django_user_model):
    """
    Create a test user.
    """
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
