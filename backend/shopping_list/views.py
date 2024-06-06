from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from authentication_app.models import UserAccount
from raw_food_item.models import Item
from raw_food_price.models import RawFoodPrice
from rest_framework import status
from .models import ShoppingList
from .serializers import ShoppingListSerializer
from django.db.models import Max
import json

# Function to add item to users shopping list 
@api_view(['POST'])
def add_to_shopping_list(request):
    # Extract data from request
    user_id = request.data.get('user_id')
    item_id = request.data.get('item_id')
    quantity = request.data.get('quantity')

    try:
        # Retrieve the UserAccount instance
        user_account = UserAccount.objects.get(pk=user_id)

        # Retrieve the Item instance
        item = Item.objects.get(pk=item_id)

        # Check if the item already exists in the shopping list for the user
        existing_item = ShoppingList.objects.filter(user_id=user_account, item_id=item).exists()

        if existing_item:
            return Response({'message': 'Item already exists in the shopping list'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Create a new entry in the ShoppingList table
            shopping_list_item = ShoppingList.objects.create(
                user_id=user_account,
                item_id=item,
                quantity=quantity
            )

            # Serialize the created item
            serializer = ShoppingListSerializer(shopping_list_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Function to retrieve the items of a users shopping list
def get_shopping_list_items(request):
    # Retrieve the user ID from query parameters
    user_id = request.GET.get('userId')

    # Ensure user_id is not None before proceeding
    if user_id is not None:
        # Use the user ID to fetch shopping list items associated with the user
        shopping_list_items = ShoppingList.objects.filter(user_id=user_id)
        
        # Initialize a list to store formatted data
        formatted_data = []

        # Iterate over each shopping list item
        for shopping_list_item in shopping_list_items:
            # Fetch the item_id from the shopping list item
            item_id = shopping_list_item.item_id_id

            # Use item_id to fetch item details (item_name and predicted_price)
            item = Item.objects.get(id=item_id)
            
            # Fetch the latest prediction date for the item
            latest_prediction_date = RawFoodPrice.objects.filter(item_id=item_id).aggregate(latest_date=Max('prediction_date'))['latest_date']
            
            # Fetch the average price for the latest prediction date
            if latest_prediction_date:
                raw_food_price = RawFoodPrice.objects.filter(item_id=item_id, prediction_date=latest_prediction_date).first()
                average_price = raw_food_price.average_price if raw_food_price else None
            else:
                average_price = None
            
            # Format the data and append to the formatted_data list
            formatted_data.append({
                'id': item.id,
                'image': item.image.url if item.image else None,
                'item_name': item.item_name,
                'average_price': average_price,
                'quantity': shopping_list_item.quantity
            })

        # Return the formatted data
        return JsonResponse(formatted_data, safe=False)
    else:
        # Return an error response if user ID is not provided
        return JsonResponse({'error': 'User ID is required'}, status=400)


# Function to update details in shopping list items
@api_view(['PUT'])
def update_list_items(request):
    if request.method == 'PUT':
        try:
            # Retrieve modified items from request data
            modified_items = request.data  
            # Get user ID from query parameters
            user_id = request.query_params.get('user_id')  

            # Iterate over modified items
            for modified_item in modified_items:
                # Retrieve the ShoppingList instance
                item_id = modified_item.get('id') 
                # Filter by both item ID and user ID
                shopping_list_item = ShoppingList.objects.get(item_id=item_id, user_id=user_id)  

                # Update the quantity field
                quantity = modified_item.get('quantity')  
                shopping_list_item.quantity = quantity

                # Use serializer to update other fields
                serializer = ShoppingListSerializer(shopping_list_item, data=modified_item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response("Shopping list items updated successfully", status=status.HTTP_200_OK)
        except ShoppingList.DoesNotExist:
            return Response({'error': 'Shopping list item not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Function to delete items in shopping list 
@api_view(["DELETE"])
def delete_list_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId')
        user_id = data.get('userId')

        # Ensure that the item belongs to the authenticated user
        item = ShoppingList.objects.get(item_id=item_id, user_id=user_id)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully'})
    except ShoppingList.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)