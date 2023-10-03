import ast
import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from phonenumber_field import validators
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned

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
        'product_key_error': {'products_error': 'Products key not presented, null or empty list'},
        'product_key_not_list': {'products_error': 'Products is not list'},
        'save_order_general_error': {'order_error': 'Unable to save order'},
        'request_type_error': {'request_error': 'Bad request. The request must be in JSON format'},
        'firstname_empty_field': {'firstname_error': 'The field is required'},
        'lastname_empty_field': {'lastname_error': 'The field is required'},
        'phonenumber_empty_field': {'phonenumber_error': 'The field is required'},
        'address_empty_field': {'address_error': 'The field is required'},
        'phonenumber_incorrect_field': {'phonenumber_error': 'The phonenumber is incorrect'},
        'incorrect_product_id': {'products_error': 'Incorrect product id'},
        'firstname_not_string': {'firstname_error': 'The field is not a valid string'},
        'user_fields_empty': {'error': 'Firstname, lastname, phonenumber and address fields are required'}
    }

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
    if not isinstance(order.get('firstname'), str):
        content = errors['firstname_not_string']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    if not order.get('firstname') and not order.get('lastname')\
        and not order.get('phonenumber') and not order.get('address'):
        content = errors['user_fields_empty']
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    for field in ('firstname', 'lastname', 'phonenumber', 'address'):
        if not order.get(field):
            content = errors[f'{field}_empty_field']
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    for product in products:
        try:
            Product.objects.get(pk=product['product'])
        except ObjectDoesNotExist:
            content = errors['incorrect_product_id']
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except MultipleObjectsReturned:
            content = errors['incorrect_product_id']
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

    try:
        validators.validate_international_phonenumber(order['phonenumber'])
    except ValidationError:
        content = errors['phonenumber_incorrect_field']
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
