import logging

import requests
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from geo import fetch_coordinates
from mapapp.models import Address
from .models import Product, Order, OrderItem
from .serializers import OrderSerializer

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        },
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            },
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    products = serializer.validated_data.get('products', [])
    with transaction.atomic():
        new_order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data['lastname'],
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address'],
        )
        necessary_products = [product['product'] for product in products]
        order_items = [OrderItem(order=new_order, **fields) for fields in products]
        for index, order_item in enumerate(order_items):
            order_item.price = necessary_products[index].price
        OrderItem.objects.bulk_create(order_items)
        apikey = settings.YANDEX_APIKEY
        if not Address.objects.filter(address=new_order.address).exists():
            new_address = Address.objects.create(address=new_order.address)
            try:
                coords = fetch_coordinates(apikey, new_order.address)
                if coords is not None:
                    new_address.lon = coords[0]
                    new_address.lat = coords[1]
                    new_address.save()
            except requests.exceptions.HTTPError:
                logger.info(f'Плохой запрос:{new_order.address}')
        else:
            pass

    serialized_new_order = OrderSerializer(new_order)

    return Response(serialized_new_order.data)
