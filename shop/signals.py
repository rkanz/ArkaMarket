from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product,Banner,Category


#Product cache
@receiver([post_delete,post_save],sender=Product)
def clear_product_cache(sender,instance,**kwargs):
    cache.delete_pattern("products:list*")
    cache.delete(f"products:detail:{instance.slug}")
    cache.delete("home:index")


#Category cache
@receiver([post_delete,post_save],sender=Category)
def clear_category_cache(sender,instance,**kwargs):
    cache.delete("categories:list")
    cache.delete_pattern("products:list*")
    cache.delete("home:index")

#Home cache
@receiver([post_delete,post_save],sender=Banner)
def clear_banner_cache(sender,instance,**kwargs):
    cache.delete("home:index")

