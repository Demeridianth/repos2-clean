from django.urls import path
from .views import OilPriceListCreateView, OilPriceDetailView

urlpatterns = [
    path('prices/', OilPriceListCreateView.as_view(), name='price-list-create'),
    path('prices/<int:pk>/', OilPriceDetailView.as_view(), name='price-detail'),
]


# FOR FUNCTION BASED VIEWS (ENDPOINTS)
# urlpatterns = [
#     path('prices/<int:price_id>/', get_price_id, name='get-price-id'),
#     path('prices/', create_price, name='create-price'),
# ]