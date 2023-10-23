from django.db import models


class Address(models.Model):
    address = models.CharField(
        'адрес',
        max_length=200,
        db_index=True,
    )
    lat = models.FloatField(
        verbose_name='широта',
        null=True,
        blank=True,
    )
    lon = models.FloatField(
        verbose_name='долгота',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'адрес'
        verbose_name_plural = 'адреса'

    def __str__(self):
        return f'{self.address} ({self.lon}, {self.lat})'
