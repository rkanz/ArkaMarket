from http.client import responses

from django.shortcuts import get_object_or_404
from rest_framework import generics,status
from .serializers import (ProductListSerializer, CategorySerializer, ProductDetailSerializer, RatingSerializer,
                          ContactMessageSerializer,BannerSerializer,RegisterSerializer,ProfileSerializer,
                          ChangePasswordSerializer,LogOutSerializer,WishlistAddSerializer)
from rest_framework.permissions import AllowAny,IsAuthenticated
from shop.models import Product,Category,Rating,Banner
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


# Create your views here.
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

product_list_view=ProductListAPIView.as_view()

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset=Product.objects.select_related('category').prefetch_related('brands','gallery','sizes','colors').annotate(average_rating=Avg('ratings__score'),
        ratings_count=Count('ratings')).all()
    serializer_class=ProductDetailSerializer
    lookup_field='slug'

product_detail_view = ProductDetailAPIView.as_view()


class CategoryListAPIView(generics.ListAPIView):
    queryset=Category.objects.filter(is_active=True)
    serializer_class=CategorySerializer
category_list_view=CategoryListAPIView.as_view()


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

class MyRatingAPIView(generics.RetrieveUpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=RatingSerializer
    def get_object(self):
            slug=self.kwargs['slug']
            obj = get_object_or_404(Rating,product__slug=slug,user=self.request.user)
            self.check_object_permissions(self.request, obj)
            return obj
my_rating_view=MyRatingAPIView.as_view()


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


class ContactMessageAPIView(generics.CreateAPIView):
    serializer_class=ContactMessageSerializer
    permission_classes=[IsAuthenticated]


contact_message_view=ContactMessageAPIView.as_view()

class BannerHomeAPIView(generics.ListAPIView):
    serializer_class=BannerSerializer
    queryset=Banner.objects.filter(is_active=True).order_by('order')[:3]
banner_home_view=BannerHomeAPIView.as_view()

class RegisterAPIView(generics.CreateAPIView):
    serializer_class=RegisterSerializer
    permission_classes=[AllowAny]
auth_register_view=RegisterAPIView.as_view()

class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    permission_classes=[IsAuthenticated]
    def get_object(self):
       return self.request.user

profile_view=ProfileAPIView.as_view()

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=request.user

        if not user.check_password(
            serializer.validated_data['old_password']):
            return Response(
                {"old password":["current password is not correct."]
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
                    "detail":"Invalid refresh token ."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

logout_view=LogOutAPIView.as_view()

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


