from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Category
from raw_food_item.models import Item
from raw_food_price.models import RawFoodPrice
from .serializers import CategorySerializer
from raw_food_item.serializers import ItemSerializer
from raw_food_price.serializers import RawFoodPriceSerializer
from rest_framework.response import Response
import json
from rest_framework import status

# View to retrieve all categories
@api_view(['GET'])
def get_categories(request):
    try:
        categories = Category.objects.order_by('-id').values('id', 'name')
        return JsonResponse(list(categories), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# View to add a new category  
@api_view(['POST'])
def add_category(request):
    if request.method == 'POST':
        # Extract category name from request data
        category_name = request.data.get('category_name')
        if category_name:
            # Create a new category instance
            category = Category.objects.create(name=category_name)
            # Serialize the created category
            serializer = CategorySerializer(category)
            return Response(serializer.data, status=201)
        else:
            return Response({'error': 'Category name is required'}, status=400)
    else:
        return Response({'error': 'Method not allowed'}, status=405)


# View to filter items by a specific category
@api_view(['GET'])
def filter_items_by_category(request):
    category_id = request.query_params.get('category')
    if category_id is not None:
        try:
            # Retrieve items belonging to the specified category
            items = Item.objects.filter(category_id=category_id)

            # Serialize the retrieved items
            item_serializer = ItemSerializer(items, many=True)

            # Retrieve category details
            category = Category.objects.get(id=category_id)
            category_serializer = CategorySerializer(category)

            # Retrieve price data from RawFoodPrice for the items
            price_data = RawFoodPrice.objects.filter(item_id__in=items.values_list('id', flat=True))
            price_serializer = RawFoodPriceSerializer(price_data, many=True)

            # Construct a mapping of item IDs to price information
            price_info_map = {price['item']: price for price in price_serializer.data}

            # Include category name and price data in each item
            for item in item_serializer.data:
                item['category_name'] = category_serializer.data['name']
                price_info = price_info_map.get(item['id'])
                if price_info:
                    item['minimum_price'] = price_info.get('minimum_price')
                    item['maximum_price'] = price_info.get('maximum_price')
                    item['average_price'] = price_info.get('average_price')
                    item['predicted_price'] = price_info.get('predicted_price')
                else:
                    # If no price data found for the item, set prices to None
                    item['minimum_price'] = None
                    item['maximum_price'] = None
                    item['average_price'] = None
                    item['predicted_price'] = None

                # Include unit along with the quantity
                item['item__quantity'] = f"{item['quantity']} {item['unit']}"

            # Prepare the response data
            response_data = {
                'items': item_serializer.data,
                'category': category_serializer.data,
            }

            return Response(response_data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response("Category ID parameter is required.", status=status.HTTP_400_BAD_REQUEST)


# View to search for categories by name
@api_view(['GET'])
def search_categories(request):
    query = request.GET.get('query', '')

    if query:
        # Search for categories containing the given query string
        categories = Category.objects.filter(name__icontains=query)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    else:
        # Return an empty list if no query is provided
        return Response([])  


# View to update details of a category
@api_view(['PUT'])
def update_category(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            category_data = data.get('category')
            if category_data:
                category_id = category_data.get('id')
                category_name = category_data.get('name')
                if category_id:
                    try:
                        # Retrieve the category instance to be updated
                        category = Category.objects.get(id=category_id)
                        # Update category name
                        category.name = category_name
                        # Save the updated categor
                        category.save()
                        # Serialize the updated category
                        serializer = CategorySerializer(category)
                        return JsonResponse(serializer.data, status=200)
                    except Category.DoesNotExist:
                        return JsonResponse({'error': 'Category does not exist'}, status=404)
                else:
                    return JsonResponse({'error': 'Category ID not provided'}, status=400)
            else:
                return JsonResponse({'error': 'Category data not provided'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# View to delete a category
@api_view(['DELETE'])
def delete_category(request):
    if request.method == 'DELETE':
        category_id = request.data.get('categoryId')
        if category_id:
            try:
                # Retrieve the category instance to be deleted
                category = Category.objects.get(id=category_id)
                # Delete the category
                category.delete()
                return Response({'message': 'Category deleted successfully'}, status=200)
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=404)
        else:
            return Response({'error': 'Category ID is required'}, status=400)
    else:
        return Response({'error': 'Method not allowed'}, status=405)
