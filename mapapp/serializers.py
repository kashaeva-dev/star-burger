from rest_framework.serializers import ModelSerializer

from mapapp.models import Address


class AddressSerializer(ModelSerializer):
    class Meta:
        model = Address
        fields = ['lon', 'lat']
