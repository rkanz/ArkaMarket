from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
from django.conf import settings

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=20,blank=True)
    address=models.TextField(blank=True)
    favorites_products=models.ManyToManyField('shop.product',blank=True,related_name='favorited_by')

    def __str__(self):
        return self.user.username
