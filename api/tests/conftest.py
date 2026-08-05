import pytest
from shop.models import Category,Product,Brand
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient

@pytest.fixture
def category():
    return Category.objects.create(name="Shoes")

@pytest.fixture
def products(category):

    nike=Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=category,
        minimum_stock=1,
    )
    adidas=Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=300,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=category,
        minimum_stock=1,
    )
    return nike,adidas

@pytest.fixture
def categorized_products():
    shoes=Category.objects.create(name="Shoes")
    shirts=Category.objects.create(name="Shirts")
    Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=shoes,
        minimum_stock=1,
        discount_percentage=10
    )
    Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=300,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=shoes,
        minimum_stock=1,
        discount_percentage=0
    )
    Product.objects.create(
        name="Polo Shirt",
        description="T-shirt",
        price=500,
        stock_quantity=3,
        image="test.jpg",
        slug="Polo",
        category=shirts,
        minimum_stock=1,
        discount_percentage=20
    )
    return shoes,shirts
@pytest.fixture
def brand_products():
    shoes = Category.objects.create(name="Shoes")
    nike = Brand.objects.create(name="Nike")
    adidas = Brand.objects.create(name="Adidas")
    nike_air = Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=shoes,
        minimum_stock=1,)
    nike_air.brands.add(nike)
    adidas_boot=  Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=300,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=shoes,
        minimum_stock=1,)
    adidas_boot.brands.add(adidas)
    return {
        "nike":nike,
        "adidas":adidas,
        "adidas_boot":adidas_boot,
        "nike_air":nike_air
    }

@pytest.fixture
def auth_client():
    user=User.objects.create_user(
        username="testuser",
        password="StrongPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    return client

