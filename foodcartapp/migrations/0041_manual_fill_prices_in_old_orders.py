from django.db import migrations


def fill_prices_in_old_orders(apps, schema_editor):
    order_item_model = apps.get_model('foodcartapp', 'OrderItem')
    order_items_to_update = order_item_model.objects.select_related('product').filter(price__isnull=True)
    for item in order_items_to_update.iterator():
        item.price = item.product.price
        item.save()
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20231013_1144'),
    ]

    operations = [
        migrations.RunPython(fill_prices_in_old_orders),
    ]
