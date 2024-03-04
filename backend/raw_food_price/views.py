# from django.db import models
# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .models import RawFoodPrice
# from raw_food_item.models import Item
# from .serializers import RawFoodPriceSerializer
# from django.views.decorators.csrf import csrf_exempt
# from django.db import connection


# # @csrf_exempt
# @api_view(['POST'])
# def add_item_price(request):
#     if request.method == 'POST':
#         # Extract data from the request
#         item_name = request.data.get('item_name')
#         minimum_price = request.data.get('minimum_price')
#         maximum_price = request.data.get('maximum_price')
#         average_price = request.data.get('average_price')
#         predicted_price = request.data.get('predicted_price')
#         prediction_date = request.data.get('prediction_date')
        
#         # Check if all required data is provided
#         if not all([item_name, minimum_price, maximum_price, average_price, predicted_price, prediction_date]):
#             return JsonResponse({'error': 'All fields are required'}, status=400)
        
#         # Use parameterized query to prevent SQL injection
#         cursor = connection.cursor()
#         cursor.execute('SELECT id FROM public.raw_food_item_item WHERE item_name = %s', [item_name])
#         row = cursor.fetchone()

#         try:
#             # Fetch the item from raw_food_item table based on item_name
#             item = Item.objects.get(item_name=item_name)
#         except Item.DoesNotExist:
#             return JsonResponse({'error': 'Item not found'}, status=404)
        
#         try:
#             # Create a new RawFoodPrice object with the fetched item and provided data
#             raw_food_price = RawFoodPrice.objects.create(
#                 item=item,
#                 minimum_price=minimum_price,
#                 maximum_price=maximum_price,
#                 average_price=average_price,
#                 predicted_price=predicted_price,
#                 prediction_date=prediction_date
#             )
#             # Return success response with the created raw_food_price data
#             serializer = RawFoodPriceSerializer(raw_food_price)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import RawFoodPrice
from raw_food_item.models import Item
from .serializers import RawFoodPriceSerializer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_exempt
from django.db import connection


@csrf_exempt
@api_view(['POST'])
def add_item_price(request):
    if request.method == 'POST':
        # Extract data from the request
        item_name = request.data.get('item_name')
        minimum_price = request.data.get('minimum_price')
        maximum_price = request.data.get('maximum_price')
        average_price = request.data.get('average_price')
        predicted_price = request.data.get('predicted_price')
        # Implementing prediction_date as current date
        from datetime import datetime
        prediction_date = datetime.now()
        
        # Check if all required data is provided
        if not all([item_name, minimum_price, maximum_price, average_price, predicted_price]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        # Use parameterized query to prevent SQL injection
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM public.raw_food_item_item WHERE item_name = %s', [item_name])
        row = cursor.fetchone()

        if row:
            item_id = row[0]
            
            try:
                # Create a new RawFoodPrice object with the fetched item and provided data
                raw_food_price = RawFoodPrice.objects.create(
                    minimum_price=minimum_price,
                    maximum_price=maximum_price,
                    average_price=average_price,
                    predicted_price=predicted_price,
                    prediction_date=prediction_date,
                    item_id=item_id,
                )
                # Return success response with the created raw_food_price data
                serializer = RawFoodPriceSerializer(raw_food_price)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Item not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
