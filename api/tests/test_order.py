from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from .conftest import auth_client
from order.models import Order,OrderItem
from cart.models import Cart
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_create_order_success(auth_client,products):
    nike,_=products
    client=auth_client
    client.post(reverse("cart-view"),{
        "product_id":nike.id,
        "quantity":3
    },format="json")
    response=client.post(reverse("orders"))
    assert response.status_code == 201
    assert response.data["status"] == "pending"
    assert Order.objects.count() == 1
    assert OrderItem.objects.count() == 1
    order=Order.objects.first()
    assert order.address is not None
    assert order.phone is not None
    nike.refresh_from_db()
    assert nike.stock_quantity == 2
    cart=Cart.objects.get(user=order.user)
    assert cart.items.count() == 0


@pytest.mark.django_db
def test_order_empty_cart(auth_client):
    response=auth_client.post(reverse("orders"))
    assert response.status_code == 400
    assert response.data["detail"] == "Cart is empty."


@pytest.mark.django_db
def test_get_orders(auth_client,products):
    nike,_=products
    auth_client.post(reverse("cart-view"),{
        "product_id":nike.id
    },format="json")
    auth_client.post(reverse("orders"))
    response=auth_client.get(reverse("orders"))
    assert response.status_code == 200
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_order_detail(auth_client,products):
    nike,_=products
    auth_client.post(reverse("cart-view"),{
        "product_id":nike.id,
        "quantity":2
    },format="json")
    auth_client.post(reverse("orders"))
    order=Order.objects.first()
    response=auth_client.get(reverse("order-detail",args=[order.id]))
    assert response.status_code == 200
    assert response.data["id"] == order.id
    assert len(response.data["items"]) == 1
    assert response.data["items"][0]["product"]["id"] == nike.id
    assert response.data["status"] == "pending"

@pytest.mark.django_db
def test_order_detail_requires_authentication(products):
    client=APIClient()
    response=client.get(reverse("order-detail",args=[1]))
    assert response.status_code == 403