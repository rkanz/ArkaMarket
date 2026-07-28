# Persian Clothing Store

A full-stack e-commerce project built with **Django** and **Django REST Framework** as a portfolio project.

The project started as a traditional Django application using Django Templates and was later extended with a RESTful API. It demonstrates both server-rendered web development and modern backend API development with JWT authentication.

---

# Features

## Web Application (Django Templates)

- User registration, login and logout
- User profile management
- Product catalog
- Product detail pages
- Shopping cart
- Wishlist
- Product rating system
- Contact form
- Featured banners
- Product search
- Responsive Bootstrap interface

---

## REST API (Django REST Framework)

### Authentication

- User registration
- JWT Authentication
- Access Token
- Refresh Token
- Token Refresh
- Logout (Refresh Token Blacklist)
- Change Password
- User Profile API

### Products

- Product list
- Product detail
- Product search
- Advanced filtering
- Ordering
- Pagination

### Ratings

- List product ratings
- Create rating
- Update current user's rating
- Rating summary
- Average rating
- Rating count

### Wishlist

- View wishlist
- Add product
- Remove product

### Shopping Cart

- View cart
- Add product to cart
- Update cart item quantity
- Remove cart item
- Clear cart
- Automatic total calculation
- Stock validation

### Orders

- Create order from cart
- View order history
- View order details
- Store purchased product prices
- Automatic stock update after purchase

### Other APIs

- Categories API
- Banner API
- Contact Message API

---

# Filtering

Products can be filtered by:

- Category
- Brand
- Gender
- Availability
- Featured products
- Discounted products
- Minimum price
- Maximum price

---

# Search

Products can be searched by:

- Product name
- Slug
- Category
- Brand
- Description

---

# Ordering

Products can be ordered by:

- Price
- Created date
- Average rating
- Number of ratings
- Featured products

---

# Technologies

- Python
- Django
- Django REST Framework
- Simple JWT
- django-filter
- SQLite
- HTML
- CSS
- JavaScript
- Bootstrap
- Pillow
- Git
- GitHub

---

# Main Database Models

- User
- Profile
- Product
- Category
- Brand
- Rating
- Cart
- CartItem
- Order
- OrderItem
- Banner
- ContactMessage

---

# Main API Endpoints

## Authentication

```http
POST   /api/auth/register/
POST   /api/token/
POST   /api/token/refresh/
POST   /api/auth/logout/

GET    /api/auth/profile/
PATCH  /api/auth/profile/

POST   /api/auth/change-password/
```

## Products

```http
GET    /api/products/
GET    /api/products/<slug>/
```

## Ratings

```http
GET    /api/products/<slug>/ratings/
POST   /api/products/<slug>/ratings/

GET    /api/products/<slug>/ratings/my-rating/
PATCH  /api/products/<slug>/ratings/my-rating/

GET    /api/products/<slug>/ratings/summary/
```

## Wishlist

```http
GET     /api/wishlist/
POST    /api/wishlist/
DELETE  /api/wishlist/<product_id>/
```

## Cart

```http
GET     /api/cart/
POST    /api/cart/

PATCH   /api/cart/items/<item_id>/
DELETE  /api/cart/items/<item_id>/

DELETE  /api/cart/clear/
```

## Orders

```http
GET     /api/orders/
POST    /api/orders/

GET     /api/orders/<order_id>/
```

## Other

```http
GET     /api/categories/
GET     /api/home/

POST    /api/contact/
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

- Django
- Django REST Framework
- RESTful API Design
- JWT Authentication
- Generic Views
- APIView
- Serializers
- Authentication & Permissions
- Filtering, Searching & Ordering
- Pagination
- Query Optimization (`select_related`, `prefetch_related`, `annotate`)
- Django ORM
- Business Logic Implementation
- Shopping Cart & Order Management
- Inventory Validation
- Git & GitHub

---

# Future Improvements

- Order cancellation
- Payment Gateway Integration
- Product Reviews & Comments
- Coupon & Discount Codes
- Swagger / OpenAPI Documentation
- Automated Testing
- PostgreSQL
- Docker
- Deployment

---

# Note

This project was developed for educational and portfolio purposes. It demonstrates both a complete Django web application and a RESTful backend API built with Django REST Framework.