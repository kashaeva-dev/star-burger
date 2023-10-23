from rest_framework.serializers import ModelSerializer, CharField, IntegerField, FloatField

from mapapp.serializers import AddressSerializer
from .models import Order, OrderItem, Restaurant


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
