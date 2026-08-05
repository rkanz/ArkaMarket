from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from .conftest import auth_client,products

@pytest.mark.django_db
def test_add_to_wishlist(auth_client,products):
    nike,_=products
    response=auth_client.post(reverse("wishlist"),{
        "product_id":nike.id
    },format="json")
    assert response.status_code == 201
    assert len(response.data) == 1
    assert response.data["detail"] == "Product added to wishlist."

@pytest.mark.django_db
def test_add_same_product_to_wishlist(auth_client,products):
    nike,_=products
    auth_client.post(reverse("wishlist"), {
        "product_id": nike.id})
    response = auth_client.post(reverse("wishlist"), {
        "product_id": nike.id
    }, format="json")
    assert response.status_code == 400
    assert response.data["detail"] == "Product is already in wishlist."

@pytest.mark.django_db
def test_add_wishlist_requires_authentication(products):
    nike,_=products
    client=APIClient()
    response=client.post(reverse("wishlist"),{
        "product_id":nike.id
    },format="json")
    assert response.status_code == 403

@pytest.mark.django_db
def test_delete_product_from_wishlist(products,auth_client):
    nike,_=products
    auth_client.post(reverse("wishlist"),{
        "product_id":nike.id
    },format="json")
    response=auth_client.delete(reverse("wishlist-detail",kwargs={
        "product_id":nike.id
    }))
    assert response.status_code == 204

