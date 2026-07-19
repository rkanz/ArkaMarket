from django.db import models
from django.contrib.auth.models import User
from shop.models import Product
# Create your models here.

class OrderStatus(models.TextChoices):
    PENDING="pending","Pending"
    CANCELED="canceled","Canceled"
    PAID="paid","Paid"
class Order(models.Model):
    status=models.CharField(choices=OrderStatus.choices,
                            default=OrderStatus.PENDING,
                            max_length=20)
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="orders")
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address=models.TextField(blank=True)
    phone=models.CharField(max_length=20,blank=True)

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=12,decimal_places=2)

    @property
    def total_price(self):
        return self.quantity * self.price