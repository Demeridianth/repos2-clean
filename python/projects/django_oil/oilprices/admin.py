from django.contrib import admin
from .models import OilPrice

@admin.register(OilPrice)
class OilPriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'price_date', 'price', 'euro_price')
    list_filter = ('price_date',)
    search_fields = ('id',)
