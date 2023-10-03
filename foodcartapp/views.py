import ast
import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order, OrderItem


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
        }
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
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):
    order = request.data
    errors = {
        'product_key_error': {'error': 'Products key not presented, null or empty list'},
        'product_key_not_list': {'error': 'Products is not list'},
        'save_order_general_error': {'error': 'Unable to save order'},
        'request_type_error': {'error': 'Bad request. The request must be in JSON format'},
    }

    print(order)
    try:
        products = order['products']
    except KeyError:
        content = errors['product_key_error']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not products:
        content = errors['product_key_error']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not isinstance(products, list):
        content = errors['product_key_not_list']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)

    try:
        new_order = Order.objects.create(
            first_name=order['firstname'],
            last_name=order['lastname'],
            phonenumber=order['phonenumber'],
            address=order['address'],
        )
        for product in order['products']:
            product_obj = Product.objects.get(pk=product['product'])
            OrderItem.objects.create(
                order=new_order,
                product=product_obj,
                quantity=product['quantity'],
                )
    except TypeError:
        content = errors['request_type_error']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        content = errors['save_order_general_error']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(order)
