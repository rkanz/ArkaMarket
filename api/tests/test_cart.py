from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from .conftest import auth_client,products



@pytest.mark.django_db
def test_get_cart(auth_client):
    response=auth_client.get(reverse("cart-view"))
    assert response.status_code == 200
    assert response.data["items"] == []
    assert response.data["total_items"] == 0

@pytest.mark.django_db
def test_add_product_to_cart(auth_client,products):
    nike,adidas=products
    response=auth_client.post(reverse("cart-view"),{
        "product_id":nike.id,
        "quantity":2
    },format="json")

    assert response.status_code == 201
    assert response.data["detail"] ==  "Product added to cart."
    cart=response.data["cart"]
    assert cart["total_items"]== 2
    assert len(cart["items"])== 1
    assert cart["items"][0]["product"]["id"] == nike.id
    assert cart["items"][0]["quantity"] == 2

@pytest.mark.django_db
def test_add_same_product_updates_quantity(auth_client,products):
    nike,_=products
    auth_client.post(reverse("cart-view"),{
        "product_id": nike.id,
        "quantity": 2
    },format="json")

    response=auth_client.post(reverse("cart-view"),{
        "product_id": nike.id,
        "quantity": 3
    }, format="json")

    assert response.status_code == 201
    assert response.data["detail"] == "Cart updated."
    cart=response.data["cart"]
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 5
    assert cart["total_items"] == 5

@pytest.mark.django_db
def test_add_product_exceeds_stock(auth_client,products):
    nike,_=products
    response=auth_client.post(reverse("cart-view"),{
        "product_id": nike.id,
        "quantity": 30
    },format="json")
    assert response.status_code == 400
    assert response.data["quantity"][0] == f"Only {nike.stock_quantity} items are available."

@pytest.mark.django_db
def test_get_cart_requires_authentication():
    client=APIClient()
    response=client.get(reverse("cart-view"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_post_cart_requires_authentication(products):
    nike,_=products
    client=APIClient()
    response=client.post(reverse("cart-view"),{
        "product_id":nike.id,
        "quantity":2
    },format="json")
    assert response.status_code == 403