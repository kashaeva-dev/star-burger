from rest_framework.serializers import ModelSerializer, CharField, IntegerField

from .models import Product, Order, OrderItem, Restaurant


class OrderItemSerializer(ModelSerializer):
    name = CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'name', 'quantity']


class RestaurantSerializer(ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)
    total_cost = IntegerField(read_only=True)
    status_full = CharField(source='get_status_display', read_only=True)
    payment_method_full = CharField(source='get_payment_method_display', read_only=True)
    available_restaurants = RestaurantSerializer(source='get_available_restaurants', many=True, read_only=True)
    restaurant_info = RestaurantSerializer(source='restaurant', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = (
            'status',
            'comment',
            'create_at',
            'called_at',
            'delivered_at',
            'restaurant',
        )

class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
