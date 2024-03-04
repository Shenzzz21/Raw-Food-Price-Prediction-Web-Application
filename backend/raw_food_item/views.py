from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Item
from .serializers import ItemSerializer
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db import transaction
from raw_food_price.models import Item, RawFoodPrice
import datetime
import json

from django.db import connection


@api_view(['POST'])
def add_item(request):
    if request.method == 'POST':
        # Serialize the data including files
        serializer = ItemSerializer(data=request.data)
        
        if serializer.is_valid():
           # Use a transaction to ensure data integrity
            with transaction.atomic():
                # Save the serialized data to the Item table
                item_instance = serializer.save()

                # Extract the ID of the newly added item
                item_id = item_instance.id
                print('Item ID: ', item_id)

                # Retrieve the Item instance using the ID
                item = Item.objects.get(pk=item_id)

                # Extract prices from the request data
                minimum_price = request.data.get('minimum_price')
                maximum_price = request.data.get('maximum_price')
                average_price = request.data.get('average_price')
                predicted_price = request.data.get('predicted_price')
                print('Minimum Price: ', minimum_price)
                print('Maximum Price: ', maximum_price)
                print('Average Price: ', average_price)
                print('Predicted Price: ', predicted_price)

                # Create a RawFoodPrice instance and save it to the database
                price_instance = RawFoodPrice.objects.create(
                    item=item,
                    minimum_price=minimum_price,
                    maximum_price=maximum_price,
                    average_price=average_price,
                    predicted_price=predicted_price,
                    prediction_date=datetime.date.today()
                )

            # Return a success response with the serialized data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return an error response if serialization fails
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_items(request):
    # Execute SQL query to fetch items data
    with connection.cursor() as cursor:
        cursor.execute("SELECT image, item_name, category, (quantity || ' ' || unit) AS quantity, minimum_price, average_price, maximum_price, predicted_price, calories, protein, carbohydrate, fat, iron, sugar FROM public.raw_food_item_item item JOIN public.raw_food_price_rawfoodprice price ON item.id = price.item_id ORDER BY item.id DESC")
        rows = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries
    items = []
    for row in rows:
        item = {
            'image': row[0],
            'item_name': row[1],
            'category': row[2],
            'quantity': row[3],
            'minimum_price': row[4],
            'average_price': row[5],
            'maximum_price': row[6],
            'predicted_price': row[7],
            'calories': row[8],
            'protein': row[9],
            'carbohydrate': row[10],
            'fat': row[11],
            'iron': row[12],
            'sugar': row[13],
        }
        items.append(item)
    
    # Return the fetched user data as JSON response
    return JsonResponse(items, safe=False)


def prediction_page_items(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('Data: ', data)
        category = data.get('category', '')
        print('Category: ', category)
        items_data = RawFoodPrice.objects.select_related('item').filter(item__category=category).order_by('-item_id').values('item_id', 'item__image', 'item__item_name', 'predicted_price')
        items_list = list(items_data)
        print(items_list)
        return JsonResponse(items_list, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    

def get_item_data(request, item_id):
    try:
        item = get_object_or_404(Item, id=item_id)
        price_data = get_object_or_404(RawFoodPrice, item_id=item_id)
        item_data = {
            'id': item.id,
            'image': item.image.url if item.image else None,
            'item_name': item.item_name,
            'calories': item.calories,
            'protein': item.protein,
            'carbohydrate': item.carbohydrate,
            'fat': item.fat,
            'iron': item.iron,
            'sugar': item.sugar,
            'minimum_price': price_data.minimum_price,
            'maximum_price': price_data.maximum_price,
            'average_price': price_data.average_price,
            'predicted_price': price_data.predicted_price,
            # Add other fields as needed
        }
        print(item_data)
        return JsonResponse(item_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


def get_items_by_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = data.get('category')
            if category is not None:
                items = Item.objects.filter(category=category).values()
                print('Category chosen:', category)
                print(items)
                return JsonResponse(list(items), safe=False)
            else:
                return JsonResponse({'error': 'Category not provided'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_categories(request):
    if request.method == 'GET':
        categories = Item.objects.values_list('category', flat=True).distinct()
        return JsonResponse(list(categories), safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def search_items(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            try:
                # Perform case-insensitive partial match search on item_name field
                items = Item.objects.filter(item_name__icontains=query)
                item_data = []
                for item in items:
                    # Fetch predicted price from RawFoodPrice model
                    try:
                        price_data = RawFoodPrice.objects.get(item=item)
                        predicted_price = price_data.predicted_price
                    except RawFoodPrice.DoesNotExist:
                        predicted_price = None
                    
                    item_info = {
                        'item_id': item.id,
                        'item_image': item.image.url if item.image else None,
                        'item_name': item.item_name,
                        'predicted_price': predicted_price,
                        # Add more fields as needed
                    }
                    item_data.append(item_info)
                    
                if not item_data:  # If item_data is empty
                    return JsonResponse({'error': 'Item not found'}, status=404)
                return JsonResponse(item_data, safe=False)
            
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        else:
            return JsonResponse({'error': 'Query parameter "query" is required'}, status=400)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Item
import json

# @require_POST
@api_view(['PUT'])
def update_item(request):
        if request.method == 'PUT':
            try:
                data = json.loads(request.body)
                item_data = data.get('item')
                print(item_data)
                if item_data:
                    item_id = item_data.get('id')
                    print(item_id)
                    if item_id:
                        item = Item.objects.get(pk=item_id)
                        price = RawFoodPrice.objects.get(item_id=item_id)
                        # Update item details
                        item.item_name = item_data.get('name')
                        item.category = item_data.get('category')
                        item.quantity = item_data.get('quantity')
                        price.minimum_price = item_data.get('minimumPrice')
                        price.average_price = item_data.get('averagePrice')
                        price.maximum_price = item_data.get('maximumPrice')
                        price.predicted_price = item_data.get('predictedPrice')
                        item.calories = item_data.get('calories')
                        item.protein = item_data.get('protein')
                        item.carbohydrate = item_data.get('carbohydrate')
                        item.fat = item_data.get('fat')
                        item.iron = item_data.get('iron')
                        item.sugar = item_data.get('sugar')
                        # Save the updated user
                        item.save()
                        return JsonResponse({'message': 'Item updated successfully'}, status=200)
                    else:
                        return JsonResponse({'error': 'User ID is required'}, status=400)
                else:
                    return JsonResponse({'error': 'Item data is missing'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)


@api_view(['DELETE'])
def delete_item(request, item_id):
    try:
        item = get_object_or_404(Item, id=item_id)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)