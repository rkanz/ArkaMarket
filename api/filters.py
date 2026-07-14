from shop.models import Product
from django_filters import NumberFilter,BooleanFilter
import django_filters

class ProductFilter(django_filters.FilterSet):
    min_price=NumberFilter(field_name='price',lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    is_discounted=BooleanFilter(method='filter_is_discounted',label='Is discounted')
    class Meta:
        model=Product
        fields= [
            'category',
            'gender',
            'is_featured',
            'is_available',
            'brands',
        ]

    def filter_is_discounted(self, queryset, name, value):
        if value is True:
            return queryset.filter(discount_percentage__gt=0)
        elif value is False:
            return queryset.filter(discount_pecentage=0)
        return queryset
