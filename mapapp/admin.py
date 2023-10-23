from django.contrib import admin

from mapapp.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass
