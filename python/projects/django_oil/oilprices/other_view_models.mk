# Function-Based Views (FBVs) using @api_view
# oilprices/views.py
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import OilPriceSerializer, OilPriceCreateSerializer, OilPriceUpdateSerializer

# # Simulated in-memory DB
# all_prices = [
#     # Assume these are dicts or objects you defined somewhere
# ]

# @api_view(['GET'])
# def get_all_prices(request):
#     serializer = OilPriceSerializer(all_prices, many=True)
#     return Response(serializer.data)


# @api_view(['GET'])
# def get_price_id(request, price_id):
#     for price in all_prices:
#         if price['price_id'] == price_id:
#             serializer = OilPriceSerializer(price)
#             return Response(serializer.data)
#     return Response({"detail": "Price not found"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['POST'])
# def create_price(request):
#     serializer = OilPriceCreateSerializer(data=request.data)
#     if serializer.is_valid():
#         new_price_id = max(p['price_id'] for p in all_prices) + 1 if all_prices else 1
#         new_price = serializer.validated_data
#         new_price['price_id'] = new_price_id
#         all_prices.append(new_price)
#         return Response(new_price, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['PUT'])
# def update_price(request, price_id):
#     for price in all_prices:
#         if price['price_id'] == price_id:
#             serializer = OilPriceUpdateSerializer(data=request.data, partial=True)
#             if serializer.is_valid():
#                 for key, value in serializer.validated_data.items():
#                     price[key] = value
#                 return Response(price)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)


# @api_view(['DELETE'])
# def delete_price(request, price_id):
#     for idx, price in enumerate(all_prices):
#         if price['price_id'] == price_id:
#             deleted = all_prices.pop(idx)
#             return Response(deleted)
#     return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)





# Class-Based Views (CBVs) using APIView
# oilprices/views.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .serializers import OilPriceSerializer, OilPriceCreateSerializer, OilPriceUpdateSerializer

# all_prices = [
#     # Same in-memory data
# ]

# class PriceListCreateView(APIView):
#     def get(self, request):
#         serializer = OilPriceSerializer(all_prices, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = OilPriceCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             new_price_id = max(p['price_id'] for p in all_prices) + 1 if all_prices else 1
#             new_price = serializer.validated_data
#             new_price['price_id'] = new_price_id
#             all_prices.append(new_price)
#             return Response(new_price, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class PriceDetailView(APIView):
#     def get_object(self, price_id):
#         for price in all_prices:
#             if price['price_id'] == price_id:
#                 return price
#         return None
    
#     def get(self, request, price_id):
#         price = self.get_object(price_id)
#         if price:
#             serializer = OilPriceSerializer(price)
#             return Response(serializer.data)
#         return Response({"detail": "Price not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     def put(self, request, price_id):
#         price = self.get_object(price_id)
#         if price:
#             serializer = OilPriceUpdateSerializer(data=request.data, partial=True)
#             if serializer.is_valid():
#                 for key, value in serializer.validated_data.items():
#                     price[key] = value
#                 return Response(price)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     def delete(self, request, price_id):
#         for idx, price in enumerate(all_prices):
#             if price['price_id'] == price_id:
#                 deleted = all_prices.pop(idx)
#                 return Response(deleted)
#         return Response({"detail": "Record not found"}, status=status.HTTP_404_NOT_FOUND)