from rest_framework.serializers import ModelSerializer, CharField, IntegerField

from mapapp.models import Address


class AddressSerializer(ModelSerializer):
    class Meta:
        model=Address
        fields='__all__'
