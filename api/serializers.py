from shop.models import (Product,Brand,Category,ProductImage,Color,Size,Rating,
                         ContactMessage,Banner,User)
from accounts.models import Profile
from order.models import Order,OrderItem
from cart.models import Cart,CartItem
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields=['id','name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['id','name','slug','is_featured']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Color
        fields=['id','name']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Size
        fields=['id','name']


class ProductListSerializer(serializers.ModelSerializer):
    category=CategorySerializer(read_only=True)
    brands=BrandSerializer(many=True,read_only=True)
    discounted_price=serializers.DecimalField(max_digits=12,decimal_places=2,read_only=True)
    average_rating=serializers.FloatField(read_only=True)
    ratings_count=serializers.IntegerField(read_only=True)
    class Meta:
        model=Product
        fields=[
            'id',
            'name',
            'slug',
            'price',
            'discount_percentage',
            'discounted_price',
            'stock_quantity',
            'image',
            'is_available',
            'brands',
            'gender',
            'category',
            'is_featured',
            'average_rating',
            'ratings_count'
        ]
class ProductDetailSerializer(serializers.ModelSerializer):
    brands=BrandSerializer(many=True,read_only=True)
    category=CategorySerializer(read_only=True)
    gallery=ProductImageSerializer(many=True,read_only=True)
    colors=ColorSerializer(read_only=True,many=True)
    sizes=SizeSerializer(read_only=True,many=True)
    discounted_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    ratings_count = serializers.IntegerField(read_only=True)
    class Meta:
        model=Product
        fields=[
            'id',
            'name',
            'slug',
            'category',
            'brands',
            'gallery',
            'gender',
            'image',
            'is_available',
            'is_featured',
            'created_at',
            'updated_at',
            'minimum_stock',
            'stock_quantity',
            'price',
            'discount_percentage',
            'discounted_price',
            'description',
            'sizes',
            'colors',
            'average_rating',
            'ratings_count',
        ]

class RatingSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model=Rating
        fields=['id','score','username','created_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ContactMessage
        fields=['first_last_name','subject','email','message']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Banner
        fields=['id','order','subtitle','title','description','image']

class HomeSerializer(serializers.Serializer):
    banners=BannerSerializer(many=True)
    featured_products=ProductListSerializer(many=True)
    featured_categories=CategorySerializer(many=True)


class RegisterSerializer(serializers.ModelSerializer):
    password1=serializers.CharField(write_only=True,required=True,min_length=8)
    password2 = serializers.CharField(write_only=True,required=True,min_length=8)
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','password1','password2']
    def validate(self,attrs):
        if attrs['password1']!=attrs['password2']:
            raise serializers.ValidationError(
                {"password2": "Password does not match."}
            )
        return attrs
    def create(self,validated_data):
        validated_data.pop('password2')
        password=validated_data.pop('password1')
        user=User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class ProfileSerializer(serializers.ModelSerializer):
    read_only_fields=['id','email','username']
    class Meta:
        model=User
        fields=['id','username','first_name','last_name','email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True,required=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password],required=True)
    new_password2 = serializers.CharField(write_only=True,validators=[validate_password],required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({
                "new_password2": "Passwords do not match."
            })

        return attrs

class LogOutSerializer(serializers.Serializer):
    refresh=serializers.CharField()

class WishlistAddSerializer(serializers.Serializer):
    product_id=serializers.IntegerField()

class CartAddSerializer(serializers.Serializer):
    product_id=serializers.IntegerField()
    quantity=serializers.IntegerField(default=1,min_value=1)
    def validate(self,attrs):
        product=Product.objects.get(id=attrs["product_id"])
        if attrs["quantity"]>product.stock_quantity:
            raise serializers.ValidationError(
                {
                    "quantity":f"Only {product.stock_quantity} items are available."
                }
            )
        return attrs

class CartItemSerializer(serializers.ModelSerializer):
    product=ProductListSerializer(read_only=True)
    total_price=serializers.ReadOnlyField()
    class Meta:
        model=CartItem
        fields=['id','product','quantity','total_price']

class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True,read_only=True)
    grand_total=serializers.SerializerMethodField()
    total_items=serializers.SerializerMethodField()
    class Meta:
        model=Cart
        fields=['id','items','total_items','grand_total','updated_at','created_at']

    def get_total_items(self,obj)-> int:
        return sum(item.quantity for item in obj.items.all())
    def get_grand_total(self,obj)-> float:
        return sum(item.total_price for item in obj.items.all())

class CartUpdateSerializer(serializers.Serializer):
    quantity=serializers.IntegerField(min_value=1)

class OrderListSerializer(serializers.ModelSerializer):
    total_price=serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields=['id','created_at','status','total_price']
    def get_total_price(self,obj)->float:
        return sum(item.total_price for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    class Meta:
        model=OrderItem
        fields=['id','order','product','quantity','price','total_price']

class OrderDetailSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields=['id','status','created_at','phone','address','items','total_price']
    def get_total_price(self,obj)->float:
        return sum(item.total_price for item in obj.items.all())
