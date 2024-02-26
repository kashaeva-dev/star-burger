import requests
import logging
from django.db import transaction
from rest_framework.serializers import ModelSerializer, CharField, IntegerField, FloatField

from geo import fetch_coordinates
from mapapp.models import Address
from mapapp.serializers import AddressSerializer
from .models import Order, OrderItem, Restaurant


logger = logging.getLogger(__file__)


class OrderItemSerializer(ModelSerializer):
    name = CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'name', 'quantity']


class RestaurantCoordsSerializer(ModelSerializer):
    address_obj = AddressSerializer(source='get_restaurant_coords', read_only=True)

    class Meta:
        model = Restaurant
        fields = '__all__'


class RestaurantSerializer(ModelSerializer):
    address_lat = FloatField(read_only=True)
    address_lon = FloatField(read_only=True)

    class Meta:
        model = Restaurant
        fields = ['name', 'address_lat', 'address_lon']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)
    total_cost = IntegerField(read_only=True)

    def create(self, validated_data):
        products = validated_data.pop('products')
        with transaction.atomic():
            order = Order.objects.create(
                firstname=validated_data['firstname'],
                lastname=validated_data['lastname'],
                phonenumber=validated_data['phonenumber'],
                address=validated_data['address'],
            )
            necessary_products = [product['product'] for product in products]
            order_items = [OrderItem(order=order, **product) for product in products]
            for index, order_item in enumerate(order_items):
                order_item.price = necessary_products[index].price
            OrderItem.objects.bulk_create(order_items)

            if not Address.objects.filter(address=order.address).exists():
                new_address = Address.objects.create(address=order.address)
                try:
                    coords = fetch_coordinates(order.address)
                    if coords is not None:
                        new_address.lon = coords[0]
                        new_address.lat = coords[1]
                        new_address.save()
                except requests.exceptions.HTTPError:
                    logger.info(f'Плохой запрос:{order.address}')
            else:
                pass

        return order


    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products',
            'total_cost',
        ]


class OrderViewSerializer(ModelSerializer):
    total_cost = IntegerField(read_only=True)
    status_full = CharField(source='get_status_display', read_only=True)
    payment_method_full = CharField(source='get_payment_method_display', read_only=True)
    available_restaurants = RestaurantSerializer(source='get_available_restaurants', many=True, read_only=True)
    restaurant_info = RestaurantSerializer(source='restaurant', read_only=True)
    address_lat = FloatField(read_only=True)
    address_lon = FloatField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'status',
            'comment',
            'payment_method',
            'status_full',
            'payment_method_full',
            'available_restaurants',
            'restaurant_info',
            'address_lat',
            'address_lon',
            'total_cost',
        ]
        read_only_fields = (
            'status',
            'comment',
            'restaurant',
        )
