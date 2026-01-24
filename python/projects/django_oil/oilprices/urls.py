from django.urls import path
from .views import OilPriceListCreateView, OilPriceDetailView

urlpatterns = [
    path('prices/', OilPriceListCreateView.as_view(), name='price-list-create'),
    path('prices/<int:pk>/', OilPriceDetailView.as_view(), name='price-detail'),
]