from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics,status
from .serializers import (ProductListSerializer, CategorySerializer, ProductDetailSerializer, RatingSerializer,
                          ContactMessageSerializer,HomeSerializer, RegisterSerializer, ProfileSerializer,
                          ChangePasswordSerializer, LogOutSerializer, WishlistAddSerializer, CartSerializer,
                          CartAddSerializer, CartUpdateSerializer,OrderListSerializer,
                          OrderDetailSerializer)
from rest_framework.permissions import AllowAny,IsAuthenticated
from shop.models import Product,Category,Rating,Banner
from cart.models import Cart,CartItem
from order.models import Order,OrderItem
from rest_framework.response import Response
from rest_framework.filters import SearchFilter,OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django.db.models import Avg,Count
from rest_framework.views import APIView
from .filters import ProductFilter
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from accounts.tasks import send_welcome_email
from order.tasks import send_order_email
from django.core.cache import cache
from drf_spectacular.utils import (extend_schema,OpenApiResponse,OpenApiTypes,
                                   OpenApiParameter,OpenApiExample)
from rest_framework_simplejwt.views import TokenObtainPairView


@extend_schema(
    summary="List Products",
    description="""
    Return a paginated list of available products.
    Supports filtering,searching and ordering.
    Responses are cached with Redis.
    """,tags=["Products"],
    responses={
        200:ProductListSerializer(many=True),
    },parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search products by name,slug,category,brand or description.",
        ),OpenApiParameter(
            name='ordering',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by price,created_at,is_featured,is_available,average_rating or ratings_count"
            "Prefix with '-' for descending order"
        ),OpenApiParameter(
            name='min_price',
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter products with a price greater than or equal to this value.",
        ),OpenApiParameter(
            name='max_price',
            type=OpenApiTypes.NUMBER,
            location=OpenApiParameter.QUERY,
            description="Filter products with a price less than or equal to this value.",
        ),OpenApiParameter(
            name='is_discounted',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter discounted products.",
        ),OpenApiParameter(
            name='category',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter products by category ID."
        ),OpenApiParameter(
            name='brands',
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Filter products by brand ID."
        ),OpenApiParameter(
            name='is_featured',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter featured products."
        ),OpenApiParameter(
            name='is_available',
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Filter available products."
        )
    ]
)

class ProductListAPIView(generics.ListAPIView):
    queryset=Product.objects.select_related('category').prefetch_related('brands').annotate(
        average_rating=Avg('ratings__score'),
        ratings_count=Count('ratings')
    ).all()
    serializer_class=ProductListSerializer
    lookup_field='slug'
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields=['name','slug','category__name','brands__name','description']
    filterset_class=ProductFilter
    ordering_fields=['price','created_at','is_featured','is_available','average_rating','ratings_count']
    ordering=['-created_at']
    def list(self,request,*args,**kwargs):
        cache_key = f"products:{request.get_full_path()}"
        cached_data=cache.get(cache_key)
        if cached_data is not None:
            print("Response From Redis Cache")
            return Response(cached_data)
        print("Response From Database")
        queryset=self.filter_queryset(self.get_queryset())
        page=self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response=self.get_paginated_response(serializer.data)
            cache.set(cache_key,response.data,timeout=300)
            return response
        serializer=self.get_serializer(queryset,many=True)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(serializer.data)

product_list_view=ProductListAPIView.as_view()

@extend_schema(
    summary="Product Details",
    description="""
    Returns the detailed information about the specified product .
    Includes category,brand,ratings,available colors and sizes.
    """,tags=["Products"]
)
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset=Product.objects.select_related('category').prefetch_related('brands','gallery','sizes','colors').annotate(average_rating=Avg('ratings__score'),
        ratings_count=Count('ratings')).all()
    serializer_class=ProductDetailSerializer
    lookup_field='slug'

product_detail_view = ProductDetailAPIView.as_view()

@extend_schema(
    summary="List Categories",
    description="""
    Returns a list of available categories.
    Responses are cached with Redis.
    """,tags=["Categories"]
)
class CategoryListAPIView(generics.ListAPIView):
    queryset=Category.objects.filter(is_active=True)
    serializer_class=CategorySerializer
    def list(self,request,*args,**kwargs):
        cache_key='categories:list'
        cached_data=cache.get(cache_key)
        if cached_data is not None:
            print("Response From Redis Cache")
            return Response(cached_data)
        print("Response From Database")
        queryset=self.filter_queryset(self.get_queryset())
        serializer=self.get_serializer(queryset,many=True)
        cache.set(cache_key,serializer.data,timeout=300)
        return Response(serializer.data)
category_list_view=CategoryListAPIView.as_view()

@extend_schema(
    summary="Submit Product Rating",
    description="""
    Creates a new rating for the specified product.

    If the authenticated user has already rated the product,
    the existing rating will be updated instead.
    """,tags=["Ratings"]
)
class RatingListCreateAPIView(generics.ListCreateAPIView):
    serializer_class=RatingSerializer
    def get_queryset(self):
        slug=self.kwargs['slug']
        return Rating.objects.filter(product__slug=slug)
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]
    def perform_create(self,serializer):
        slug=self.kwargs['slug']
        product=get_object_or_404(Product,slug=slug)
        user=self.request.user
        if Rating.objects.filter(user=user,product=product).exists():
            raise ValidationError({
                'detail':"شما قبلا ثبت امتیاز کردید"
            })

        serializer.save(user=self.request.user,product=product)
product_rating_view=RatingListCreateAPIView.as_view()

@extend_schema(
    summary="Retrieve User Rating",
    description="""
    Creates a new rating for the specified product.

    If the user has already rated the product,
    the existing rating is updated instead.

    Authentication is required. """,
    tags=["Ratings"],
)
class MyRatingAPIView(generics.RetrieveUpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=RatingSerializer
    def get_object(self):
            slug=self.kwargs['slug']
            obj = get_object_or_404(Rating,product__slug=slug,user=self.request.user)
            self.check_object_permissions(self.request, obj)
            return obj
my_rating_view=MyRatingAPIView.as_view()

@extend_schema(
    summary="Product Rating Summary",
    description="""
    Returns the average rating and total number of ratings for a product.
    """,tags=["Rating"],
    responses={
        200:RatingSerializer
    }
)
class RatingSummaryAPIView(APIView):
    def get(self,request,*args,**kwargs):
        slug=self.kwargs['slug']
        product=get_object_or_404(Product,slug=slug)
        ratings=Rating.objects.filter(product=product)
        summary = ratings.aggregate(average_rating=Avg('score'), ratings_count=Count('id'))
        response={
            "average_rating":summary["average_rating"],
            "ratings_count":summary["ratings_count"],
        }
        return Response(response)
ratings_summary_view=RatingSummaryAPIView.as_view()

@extend_schema(
    summary="Send Contact Message",
    description="Send Message to the the site administrator ,Authentication is required",
    tags=["Contact"]
)
class ContactMessageAPIView(generics.CreateAPIView):
    serializer_class=ContactMessageSerializer
    permission_classes=[IsAuthenticated]


contact_message_view=ContactMessageAPIView.as_view()

@extend_schema(
    summary="Home Page Data",
    description="""
    Returns featured products, featured categories and active banners
    for the home page.
    Responses are cached with Redis.""",
    tags=["Home"],
    responses={
        200:HomeSerializer
    }
)
class HomeAPIView(APIView):
    def get(self,request):
        cache_key = "home:index"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            print("Response From Redis Cache")
            return Response(cached_data)
        print("Response From Database")
        featured_products=Product.objects.filter(is_featured=True,is_available=True).select_related(
            "category").prefetch_related("brands")[:3]
        featured_categories=Category.objects.filter(is_featured=True,is_active=True)[:3]
        banners=Banner.objects.filter(is_active=True).order_by('order')[:3]
        data={"banners":banners,"featured_products":featured_products,
              "featured_categories":featured_categories}
        serializer = HomeSerializer(data)
        cache.set(cache_key,serializer.data,timeout=300,)
        return Response(serializer.data)

home_view=HomeAPIView.as_view()

@extend_schema(
    summary="Register User",
    description="""
    Creates a new user account.
    A welcome email is sent asynchronously using Celery.""",
    tags=["Authentication"],
    responses={
        201:RegisterSerializer
    },
    examples=[
        OpenApiExample(
            "Register Example",
            value={
                "username":"testuser",
                "first_name":"MyName",
                "Last_name":"MyLastName",
                "email":"test@example.com",
                "password1":"StrongPassword123",
                "password2": "StrongPassword123"
            },request_only=True

        )
    ]
)
class RegisterAPIView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_welcome_email.delay(user.pk)
auth_register_view=RegisterAPIView.as_view()

@extend_schema(
    summary="User Profile",
    description="""
    Returns the authenticated user's profile.
    The profile information can also be updated.""",
    tags=["Authentication"]
)
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    permission_classes=[IsAuthenticated]
    def get_object(self):
       return self.request.user

profile_view=ProfileAPIView.as_view()


@extend_schema(
    summary="Password Change",
    description="""
    Changes the authenticated user's password.
    Authentication is required.
    The current password must be provided and validated.""",
    tags=["Authentication"],
    request=ChangePasswordSerializer,
    responses={
        400:OpenApiResponse(
            description="The current password is not correct"
        ),200:OpenApiResponse(
            description="Password changed successfully",
        )
    },examples=[
        OpenApiExample(
            "Password Change Request",
            value={
                "old_password":"hello123",
                "new_password":"StrongPassword123",
                "new_password2":"StrongPassword123"
            },request_only=True
        ),OpenApiExample(
            "Successful Response",
            value={
                "detail":"Password changed successfully."
            },response_only=True
        )
    ]
)
class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=request.user

        if not user.check_password(
            serializer.validated_data['old_password']):
            return Response(
                {"old_password":["The current password is not correct."]
                 },
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(
            serializer.validated_data["new_password"]
        )
        user.save()
        return Response(
            {
                "detail":"Password changed successfully."
            },
            status=status.HTTP_200_OK
        )

password_change_view=ChangePasswordAPIView.as_view()

@extend_schema(
    summary="Logout User",
    description="""
    Logs out the authenticated user.

    The provided refresh token is added to the blacklist.

    Authentication is required.""",
    tags=["Authentication"],
    request=LogOutSerializer,
    responses={
        400:OpenApiResponse(
            description="Invalid refresh token."
        ),200:OpenApiResponse(
            description="Logged out successfully."
        ),
    }
)
class LogOutAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer = LogOutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token=RefreshToken( serializer.validated_data["refresh"])
            token.blacklist()
            return Response(
                {
                    "detail": "Logged out successfully."
                }
            )
        except TokenError:
            return Response(
                {
                    "detail":"Invalid refresh token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

logout_view=LogOutAPIView.as_view()

@extend_schema(
    summary="Manage Wishlist",
    description="""
    Retrieves the authenticated user's wishlist.
    Allows adding and removing products from the wishlist.
    Authentication is required
    """,
    tags=["Wishlist"],
    request=WishlistAddSerializer,
    responses={
        201:OpenApiResponse(
            description="Product added to wishlist."
        )
        ,400:OpenApiResponse(
            description="Product is already in wishlist."
        ),204:OpenApiResponse(
            description="Product removed from wishlist.")
    }
)
class WishlistAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request,product_id=None):
        profile = request.user.profile
        products=profile.favorites_products.all()
        serializer = ProductListSerializer(products, many=True)

        return Response(serializer.data)
    def post(self,request,product_id=None):
        serializer=WishlistAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile=request.user.profile
        product=get_object_or_404(Product,id=serializer.validated_data["product_id"])
        if profile.favorites_products.filter(id=product.id).exists():
            return Response (
                {"detail":"Product is already in wishlist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        profile.favorites_products.add(product)
        return Response(
            {"detail" :"Product added to wishlist."},
            status=status.HTTP_201_CREATED
        )
    def delete(self,request,product_id):
        profile=request.user.profile
        product=get_object_or_404(Product,id=product_id)
        if not profile.favorites_products.filter(id=product.id).exists():
            return Response (
                {"detail":"Product is not in wishlist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        profile.favorites_products.remove(product)
        return Response(status=status.HTTP_204_NO_CONTENT)
wishlist_view=WishlistAPIView.as_view()



class CartAPIVIEW(APIView):
    permission_classes=[IsAuthenticated]
    @extend_schema(
        summary="Get Shopping Cart",
        description="""
        Retrieves the authenticated user's shopping cart .
        Authentication is required.""",
        tags=["Cart"],
        responses={
            200: CartSerializer,
        }
    )
    def get(self,request):
        cart,created=Cart.objects.get_or_create(user=request.user)
        serializer=CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(
        summary="Manage Shopping Cart",
        description="""
        Allows adding products to the shopping cart .
        Raise error if requested quantity exceeds available stock.
        Authentication is required.""",
        tags=["Cart"],
        request=CartAddSerializer,
        responses={
            400: OpenApiResponse(
                description="Requested quantity exceeds available stock."
            ), 201: OpenApiResponse(
                description="Product added or cart updated successfully"
            ),
        }, examples=[
            OpenApiExample(
                "Add Product To Cart Request",
                value={
                    "product_id": 5,
                    "quantity": 2
                }, request_only=True
            ),OpenApiExample(
                "Add Product To Cart Response",
                value={
                    "detail": "Product added to cart",
                    "cart":{
                        "id": 1,
                        "items": [
                            {
                                "id": 1,
                                "product": 5,
                                "quantity": 2,
                                "price": 5000,
                                "total_price": 10000
                            },
                            {
                                "id": 2,
                                "product": 8,
                                "quantity": 1,
                                "price": 1000,
                                "total_price": 1000
                            }
                        ],
                        "total_items": 3,
                        "grand_total": 11000,
                        "updated_at": "2026-08-01T08:01:29.619Z",
                        "created_at": "2026-08-01T08:01:29.619Z",
                    },
                },response_only=True
            )
        ]
    )
    def post(self,request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = get_object_or_404(Product,id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item,item_created = CartItem.objects.get_or_create(cart=cart,product=product)
        if item_created:
            new_quantity = quantity
        else:
            new_quantity = cart_item.quantity + quantity

        if new_quantity > product.stock_quantity:
            return Response(
                {
                    "detail": f"Only {product.stock_quantity} items are available."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.save()
        detail = (
            "Product added to cart."
            if item_created
            else "Cart updated.")

        return Response(
            {
                "detail": detail,
                "cart": CartSerializer(cart).data,
            },
            status=status.HTTP_201_CREATED,
        )
cart_view=CartAPIVIEW.as_view()


class CartItemAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        summary="Update Cart Item",
        description="""
        Updates the quantity of a specific item in the authenticated user's shopping cart.
        Returns an error if requested quantity exceeds the available stock .
        Authentication is required.""",
        tags=["Cart"],
        request=CartSerializer,
        responses={
            200:OpenApiResponse(
                description="Cart items updated."
            ),
            400:OpenApiResponse (
                description="Requested quantity exceeds available stock"
            )
        }
    )
    def patch(self,request,item_id):
        serializer = CartUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart=get_object_or_404(Cart,user=request.user)
        cart_item=get_object_or_404(CartItem,id=item_id,cart=cart)
        cart_item.quantity = serializer.validated_data["quantity"]
        if serializer.validated_data["quantity"]>cart_item.product.stock_quantity:
            return Response({
                "detail":f"Only {cart_item.product.stock_quantity} items are available."
            },status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.save()
        serializer=CartSerializer(cart)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        summary="Remove Cart Item",
        description="""
        Removes the specified item from the authenticated user's shopping cart.
        Authentication is required.""",
        tags=["Cart"],
        responses={
            204:OpenApiResponse(
                description="Item deleted from shopping cart."
            )
        }
    )
    def delete(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        cart_item.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
cart_item_view=CartItemAPIView.as_view()

@extend_schema(
    summary="Clear Shopping Cart ",
    description="""Removes all items from the authenticated user's shopping cart.
    Authentication is required.
    """,
    tags=["Cart"],
    responses={
        204:OpenApiResponse(
            description="Shopping cart cleared successfully."
        )
    }
)
class ClearCartAPIView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self,request):
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
cart_clear_view=ClearCartAPIView.as_view()


@extend_schema(
    summary="Manage Order",
    description="""
    Creates a new order from the authenticated user's shopping cart.
    Product stock is updated automatically.
    An order confirmation email is sent asynchronously using Celery.
    Authentication is required.""",
    tags=["Orders"],
    responses={
        400:OpenApiResponse(
            description="Cart is empty"
        ),201:OrderListSerializer
    },examples=[
        OpenApiExample(
            "Successful Response",
            value={
                "id": 1,
                "created_at": "2026-08-01T08:01:29.619Z",
                "status": "pending",
                "total_price": 125000
            },
            response_only=True,
        )
    ]
)
class OrderAPIView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OrderListSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

    @transaction.atomic
    def post(self, request):
        cart,_ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {
                    "detail": "Cart is empty."
                }, status=status.HTTP_400_BAD_REQUEST,
            )
        for items in cart_items:
            if items.quantity > items.product.stock_quantity:
                return Response(
                    {
                        "detail": f"Only {items.product.stock_quantity} items of {items.product.name} are available."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        order = Order.objects.create(
            user=request.user,
            address=request.user.profile.address,
            phone=request.user.profile.phone
        )
        for items in cart_items:
            OrderItem.objects.create(order=order, product=items.product, quantity=items.quantity,
                             price=items.product.discounted_price)
            items.product.stock_quantity -= items.quantity
            items.product.save(update_fields=["stock_quantity"])
        cart_items.delete()
        send_order_email.delay(order.id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED
                        )

order_view=OrderAPIView.as_view()

@extend_schema(
    summary="Order Details",
    description="""
    Returns detailed information about the specified order.
    Only the authenticated user's own orders can be accessed .
    Authentication is required .""",
    tags=["Orders"]
)
class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OrderDetailSerializer
    lookup_field = "id"
    lookup_url_kwarg = "order_id"
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
order_detail_view=OrderDetailAPIView.as_view()

@extend_schema(
    summary="User Login",
    description="Authenticated the user and return JWT access and refresh tokens.",
    tags=["Authentication"],
    examples=[
        OpenApiExample(
            "Login Request",
            value={
                "username":"testuser",
                "password":"StrongPassword123"
            },request_only=True
        ),OpenApiExample(
            "Successful Response",
            value={
                "refresh":"eyJhbGc...",
                "access":"eyJhbGc..."
            },response_only=True
        ),
    ],
)
class LoginAPIView(TokenObtainPairView):
    pass
login_view=LoginAPIView.as_view()