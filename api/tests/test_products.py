from http.client import responses

from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from shop.models import Product,Category
from .conftest import  products,categorized_products
# Create your tests here.
@pytest.mark.django_db
def test_product_list():
    category=Category.objects.create(
        name="Shoes"
    )
    product=Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=category,
        minimum_stock=1,
    )
    client=APIClient()
    url=reverse("product-list")
    response=client.get(url)
    assert response.status_code == 200
    assert len(response.data["results"])== 1
    assert response.data["results"][0]["name"]== "Nike Air"

@pytest.mark.django_db
def test_product_search():
    category = Category.objects.create(
        name="Shoes"
    )
    Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=category,
        minimum_stock=1,
    )
    Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=150,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=category,
        minimum_stock=1,
    )
    client=APIClient()
    response=client.get(reverse("product-list"),{"search":"nike"})
    assert response.status_code==200
    assert len((response.data["results"])) == 1
    assert response.data["results"][0]["name"]=="Nike Air"

@pytest.mark.django_db
def test_product_filter_max_price():
    category = Category.objects.create(
        name="Shoes"
    )
    Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=category,
        minimum_stock=1,
    )
    Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=300,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=category,
        minimum_stock=1,
    )
    client=APIClient()
    response=client.get(reverse("product-list"),{"max_price":140})
    assert response.status_code == 200
    assert len(response.data["results"])==1
    assert response.data["results"][0]["name"]=="Nike Air"

@pytest.mark.django_db
def test_product_filter_min_price():
    category = Category.objects.create(
        name="Shoes"
    )
    Product.objects.create(
        name="Nike Air",
        description="Running shoes",
        price=120,
        stock_quantity=5,
        image="test.jpg",
        slug="nike-air",
        category=category,
        minimum_stock=1,
    )
    Product.objects.create(
        name="Adidas",
        description="Football shoes",
        price=300,
        stock_quantity=5,
        image="test.jpg",
        slug="adidas",
        category=category,
        minimum_stock=1,
    )
    client=APIClient()
    response=client.get(reverse("product-list"),{"min_price":200})
    assert response.status_code == 200
    assert len(response.data["results"])==1
    assert response.data["results"][0]["name"]=="Adidas"

@pytest.mark.django_db
def test_product_ordering_by_price_asc(products):
    client=APIClient()
    response=client.get(reverse("product-list"),{"ordering":"price"})
    assert response.status_code == 200
    assert len(response.data["results"])==2
    assert response.data["results"][0]["name"]=="Nike Air"


@pytest.mark.django_db
def test_product_ordering_by_price_desc(products):
    client=APIClient()
    response=client.get(reverse("product-list"),{"ordering":"-price"})
    assert response.status_code == 200
    assert len(response.data["results"])==2
    assert response.data["results"][0]["name"]=="Adidas"


@pytest.mark.django_db
def test_product_filter_by_category(categorized_products):
    shoes,shirts=categorized_products
    client=APIClient()
    response=client.get(reverse("product-list"),{"category":shirts.id})
    assert response.status_code == 200
    assert len(response.data["results"])==1
    for product in response.data["results"]:
        assert product["category"]["id"]==shirts.id
        assert product["category"]["name"]=="Shirts"
        assert product["category"]["slug"]=="shirts"

@pytest.mark.django_db
def test_product_filter_by_brand(brand_products):
    data=brand_products
    nike=data["nike"]
    client=APIClient()
    response=client.get(reverse("product-list"),{"brands":nike.id})
    assert response.status_code==200
    assert len(response.data["results"])==1
    product=response.data["results"][0]
    assert product["name"]=="Nike Air"
    assert product["brands"][0]["id"]==nike.id


@pytest.mark.django_db
def test_product_filter_discount(categorized_products):
    shirt,shoes=categorized_products
    client=APIClient()
    response=client.get(reverse("product-list"),{"is_discounted":True})
    names = {p["name"] for p in response.data["results"]}
    assert "Nike Air" in names
    assert "Polo Shirt"in names
    assert "Adidas"not in names
    assert response.status_code == 200
    assert len(response.data["results"])==2
    for product in response.data["results"]:
        assert float(product["discount_percentage"])>0


@pytest.mark.django_db
def test_product_detail(brand_products):
    data=brand_products
    nike_air=data["nike_air"]
    client=APIClient()
    response=client.get(reverse("product-detail",kwargs={"slug":nike_air.slug}))
    assert response.status_code == 200
    assert response.data["id"] == nike_air.id
    assert response.data["name"] == nike_air.name
    assert response.data["slug"]== nike_air.slug
    assert float(response.data["price"]) == float(nike_air.price)

@pytest.mark.django_db
def test_product_detail_not_found():
    client=APIClient()
    response=client.get(reverse("product-detail",kwargs={"slug":"not-exist"}))
    assert response.status_code == 404