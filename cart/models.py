from django.db import models
from shop.models import Product
from django.contrib.auth.models import User

# Create your models here.
class Cart(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,related_name='items',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,related_name='cart_items',on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product"],
                name="unique_cart_product"
            )
        ]
    @property
    def total_price(self)->float:
        return self.quantity * self.product.discounted_price