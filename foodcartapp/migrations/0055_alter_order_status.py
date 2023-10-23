# Generated by Django 3.2.15 on 2023-10-16 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('1_NEW', 'Необработанный'), ('2_COOKING', 'Готовится'), ('3_DELIVERY', 'Доставляется'), ('4_CLOSED', 'Завершен')], db_index=True, default='1_NEW', max_length=15, verbose_name='статус'),
        ),
    ]