import logging

import requests
from django import forms
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.encoding import iri_to_uri
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from geo import fetch_coordinates
from mapapp.models import Address
from star_burger.settings import ALLOWED_HOSTS
from .models import Product, Order, OrderItem
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline,
    ]

    def save_model(self, request, obj, form, change):
        apikey = settings.YANDEX_APIKEY
        if not Address.objects.filter(address=obj.address).exists():
            new_address = Address.objects.create(address=obj.address)
            try:
                coords = fetch_coordinates(apikey, obj.address)
                if coords is not None:
                    new_address.lon = coords[0]
                    new_address.lat = coords[1]
                    new_address.save()
            except requests.exceptions.HTTPError:
                logger.info(f'Плохой запрос:{obj.address}')
        else:
            pass
        super(RestaurantAdmin, self).save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline,
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ],
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide',
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            ),
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def save_formset(self, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            product = Product.objects.get(pk=instance.pk)
            instance.price = product.price
            instance.save()
        formset.save_m2m()

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(OrderAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['restaurant'].queryset = self.instance.get_available_restaurants(list_for='admin')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = (
        'id',
        'firstname',
        'lastname',
        'phonenumber',
        'address',
        'status',
    )
    inlines = (
        OrderItemInline,
    )

    def response_post_save_change(self, request, obj):
        res = super().response_post_save_change(request, obj)
        next_url = request.GET['next']
        if next_url and url_has_allowed_host_and_scheme(request.GET['next'], None):
            return HttpResponseRedirect(iri_to_uri(request.GET['next']))
        else:
            return res


    def save_model(self, request, obj, form, change):
        if obj.restaurant and obj.status == 'NEW':
            obj.status = 'COOKING'

        apikey = settings.YANDEX_APIKEY
        if not Address.objects.filter(address=obj.address).exists():
            new_address = Address.objects.create(address=obj.address)
            try:
                coords = fetch_coordinates(apikey, obj.address)
                if coords is not None:
                    new_address.lon = coords[0]
                    new_address.lat = coords[1]
                    new_address.save()
            except requests.exceptions.HTTPError:
                logger.info(f'Плохой запрос:{obj.address}')
        else:
            pass
        super().save_model(request, obj, form, change)
