from rest_framework import generics
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import OilPrice
from .serializers import OilPriceSerializer

# to run: python manage.py runserver
# for swagger: http://127.0.0.1:8000/api/docs/
# for superuser ui: python manage.py createsuperuser


class OilPriceListCreateView(generics.ListCreateAPIView):
    queryset = OilPrice.objects.all()       #This tells Django where the data comes from #It is the base database query for this view
    serializer_class = OilPriceSerializer   #Convert model → JSON (GET)  Validate JSON → model (POST)

    filter_backends = [DjangoFilterBackend, OrderingFilter]     #They are plugins that modify the queryset before execution.
    # GET /api/prices/?price=100
    # GET /api/prices/?price_date=2024-01-01

    filterset_fields = ['id', 'price_date', 'price', 'euro_price']  # “Users may filter only by THESE fields.”

    ordering_fields = ['id', 'price_date', 'price', 'euro_price']   # Enables sorting via query params.
    # /api/prices/?ordering=price
    # /api/prices/?ordering=-price
    # /api/prices/?ordering=price_date

class OilPriceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OilPrice.objects.all()
    serializer_class = OilPriceSerializer

    def get_object(self):
        try:
            return OilPrice.objects.get(pk=self.kwargs['pk'])
        except OilPrice.DoesNotExist:
            raise NotFound('Record not found')
        



