from django.db.models import Count, Subquery, OuterRef

from foodcartapp.models import Order, Restaurant
from mapapp.models import Address

if __name__=="__main__":
    order = Order.objects.filter(pk=2).first()
    available_restaurants = Restaurant.objects.filter(
        menu_items__product__in=order.products.all().values_list('product', flat=True),
        menu_items__availability=True,
    ).annotate(
        num_order_items=Count('menu_items__product')
    ).filter(
        num_order_items=len(order.products.all())
    ).distinct(

    ).annotate(
        address_lon=Subquery(
            Address.objects.filter(address=OuterRef('address')).values('lon')[:1]
        )
    ).annotate(
        address_lat=Subquery(
            Address.objects.filter(address=OuterRef('address')).values('lat')[:1]
        )
    )
    print(available_restaurants)
