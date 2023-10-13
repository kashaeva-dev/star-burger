from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import QuerySet, Prefetch, Sum, Count, F
from phonenumber_field.modelfields import PhoneNumberField



class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def orders_with_total_cost_and_prefetched_products(self):
        return self.prefetch_related(
            Prefetch(
                'products',
                queryset=OrderItem.objects.select_related('product'),
            )).annotate(
            total_cost=Sum(F('products__price') * F('products__quantity'))
            ).all()


class Order(models.Model):
    STATUSES = [
        ('new', 'Необработанный'),
        ('cooking', 'Готовится'),
        ('delivery', 'Доставляется'),
        ('closed', 'Завершен'),
    ]
    firstname = models.CharField(
        max_length=40,
        verbose_name='имя',
    )
    lastname = models.CharField(
        max_length=40,
        verbose_name='фамилия',
    )
    phonenumber = PhoneNumberField(blank=False)
    address = models.TextField(
        verbose_name='адрес доставки',
        default=True,
    )
    status = models.CharField(
        verbose_name='статус',
        max_length=15,
        choices=STATUSES,
        default='new',
        db_index=True,
        null=False,
    )
    comment = models.TextField(
        verbose_name='комментарий к заказу',
        blank=True,
    )
    registered_at = models.DateTimeField(
        verbose_name='дата создания',
        auto_now_add=True,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='дата звонка',
        null=True,
        blank=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='дата доставки',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.pk}: {self.registered_at.strftime('%d.%m.%Y')} - {self.address}"

    objects = OrderQuerySet.as_manager()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='products',
        verbose_name='заказ',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='продукт',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество',
        default=1,
    )
    price = models.DecimalField(
        verbose_name='цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'пункт заказа'
        verbose_name_plural = 'пункты заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return f"{self.order.pk}: {self.product.name} - {self.quantity}"
