from rest_framework import serializers
from .models import OilPrice

class OilPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = OilPrice                # Which model this serializer is for
        fields = ['id', 'price_date', 'price', 'euro_price']  # Fields to include in API



# It defines Serializers, which are responsible for:

# Converting Django model instances to JSON (or other formats) for API responses.

# Validating and converting incoming JSON data into Django model instances or Python objects for saving.

# Think of serializers as the bridge between your Django ORM models and the data sent over the network (JSON).