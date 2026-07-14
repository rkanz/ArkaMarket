# Persian Clothing Store

A full-stack e-commerce project built with Django and Django REST Framework as a portfolio project.

The project started as a traditional Django web application using Django Templates and was later extended with a RESTful API using Django REST Framework. It demonstrates both server-rendered web development and modern backend API development.

---

# Features

## Web Application (Django Templates)

* User registration, login and logout
* User profile management
* Product catalog
* Product detail pages
* Shopping cart
* Favorites (Wishlist)
* Product rating system
* Contact form
* Featured banners
* Product search
* Responsive Bootstrap interface

---

## REST API (Django REST Framework)

### Authentication

* User registration
* JWT Authentication
* Access Token
* Refresh Token
* Token Refresh
* Logout (Refresh Token Blacklist)
* Change Password
* User Profile API

### Products

* Product list
* Product detail
* Product search
* Advanced filtering
* Ordering
* Pagination

### Ratings

* List product ratings
* Create rating
* Update current user's rating
* Rating summary
* Average rating
* Rating count

### Wishlist

* View wishlist
* Add products to wishlist
* Remove products from wishlist

### Other APIs

* Categories API
* Banner API
* Contact Message API

---

# Filtering

Products can be filtered by:

* Category
* Brand
* Gender
* Availability
* Featured products
* Discounted products
* Minimum price
* Maximum price

---

# Search

Products can be searched by:

* Product name
* Slug
* Category
* Brand
* Description

---

# Ordering

Products can be ordered by:

* Price
* Created date
* Average rating
* Number of ratings
* Featured products

---

# Technologies

* Python
* Django
* Django REST Framework
* Simple JWT
* django-filter
* SQLite
* HTML
* CSS
* JavaScript
* Bootstrap
* Pillow
* Git
* GitHub

---

# Main Database Models

* User
* Profile
* Product
* Category
* Brand
* Rating
* Banner
* ContactMessage

---

# Main API Endpoints

## Authentication

```
POST   /api/auth/register/
POST   /api/token/
POST   /api/token/refresh/
POST   /api/auth/logout/

GET    /api/auth/profile/
PATCH  /api/auth/profile/

POST   /api/auth/change-password/
```

## Products

```
GET    /api/products/
GET    /api/products/<slug>/
```

## Ratings

```
GET    /api/products/<slug>/ratings/
POST   /api/products/<slug>/ratings/

GET    /api/products/<slug>/ratings/my-rating/
PATCH  /api/products/<slug>/ratings/my-rating/

GET    /api/products/<slug>/ratings/summary/
```

## Wishlist

```
GET     /api/wishlist/
POST    /api/wishlist/
DELETE  /api/wishlist/<product_id>/
```

## Other

```
GET    /api/categories/
GET    /api/banners/
POST   /api/contact/
```

---

## Screenshots

### Home Page
![Home Page](screenshots/home.png)

### Shop Page
![Shop Page](screenshots/shop.png)

### Product Details
![Product Details](screenshots/product_detail.png)

### Cart
![Cart](screenshots/cart.png)

### Favorites
![Favorites](screenshots/favorite.png)

### Profile
![Profile](screenshots/user_profile.png)

---

# What I Learned

During this project I gained practical experience with:

* Django
* Django REST Framework
* JWT Authentication
* RESTful API Design
* Generic Views
* APIView
* Serializers
* Authentication & Permissions
* Filtering, Searching & Ordering
* Query Optimization (`select_related`, `prefetch_related`, `annotate`)
* Pagination
* Django ORM
* Git & GitHub

---

# Future Improvements

* Shopping Cart API
* Order API
* Checkout process
* Payment Gateway Integration
* Product Reviews & Comments
* Inventory Management
* Swagger / OpenAPI Documentation
* Automated Testing
* Docker
* Deployment

---

# Note

This project was developed for educational and portfolio purposes. It demonstrates both a complete Django web application and a RESTful backend API built with Django REST Framework.
