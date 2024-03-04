# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ShoppingList
from authentication_app.models import UserAccount
from raw_food_item.models import Item
from .serializers import ShoppingListSerializer
from rest_framework import status


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

# @api_view(['POST'])
# def add_to_shopping_list(request):
#     # Extract data from request
#     user_id = request.data.get('user_id')
#     item_id = request.data.get('item_id')
#     quantity = request.data.get('quantity')

#     # Retrieve the UserAccount instance
#     user_account = UserAccount.objects.get(pk=user_id)

#     # Retrieve the Item instance
#     item = Item.objects.get(pk=item_id)

#     # Create a new entry in the ShoppingList table
#     shopping_list_item = ShoppingList.objects.create(
#         user_id=user_account,
#         item_id=item,
#         quantity=quantity
#     )

#     # Serialize the created item
#     serializer = ShoppingListSerializer(shopping_list_item)

#     return Response(serializer.data)



# @api_view(['POST'])
# def add_to_shopping_list(request):
#     # Extract data from request
#     user_id = request.data.get('user_id')
#     item_id = request.data.get('item_id')
#     quantity = request.data.get('quantity')

#     try:
#         # Check if the item already exists in the shopping list for the user
#         existing_item = ShoppingList.objects.filter(user_id=user_id, item_id=item_id).exists()
        
#         if existing_item:
#             return Response({'message': 'Item already exists in the shopping list'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             # Create a new entry in the ShoppingList table
#             shopping_list_item = ShoppingList.objects.create(
#                 user_id=user_id,
#                 item_id=item_id,
#                 quantity=quantity
#             )

#             # Serialize the created item
#             serializer = ShoppingListSerializer(shopping_list_item)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import connection
from django.http import JsonResponse

def get_shopping_list_items(request):
    # Retrieve the user ID from query parameters
    user_id = request.GET.get('userId')
    print('User ID:', user_id)

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
            print('Item ID:', item_id)

            # Use item_id to fetch item details (item_name and predicted_price)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT item.id, image, item_name, average_price, list.quantity
                    FROM public.raw_food_price_rawfoodprice AS price
                    JOIN public.raw_food_item_item AS item
                    ON item.id = price.item_id
                    JOIN public.shopping_list_shoppinglist list
                    ON item.id  = list.item_id_id
                    WHERE item.id = %s
                """, [item_id])
                # Fetch the row
                row = cursor.fetchone()

            # Check if the row is not None
            if row is not None:
                # Format the data and append to the formatted_data list
                formatted_data.append({
                    'id': row[0],
                    'image': row[1],
                    'item_name': row[2],
                    'average_price': row[3],
                    'quantity': row[4]
                })

                print(formatted_data)

        # Return the formatted data
        return JsonResponse(formatted_data, safe=False)
    else:
        # Return an error response if user ID is not provided
        return JsonResponse({'error': 'User ID is required'}, status=400)



# @api_view(['PUT'])
# def update_shopping_list_items(request):
#     if request.method == 'PUT':
#         try:
#             # Retrieve item IDs from query parameters
#             item_ids = request.query_params.getlist('item_ids')
#             print(item_ids)

#             # Retrieve modified items from request data
#             modified_items = request.data
#             print(modified_items)

#             # Iterate over item IDs and corresponding modified data
#             for item_id, item_data in zip(item_ids, modified_items):
#                 # Retrieve the ShoppingList instance
#                 shopping_list_item = ShoppingList.objects.get(pk=item_id)

#                 # Update the item_active field based on the 'isChecked' value in item_data
#                 if 'isChecked' in item_data:
#                     shopping_list_item.item_active = not item_data['isChecked']

#                 # Use serializer to update other fields
#                 serializer = ShoppingListSerializer(shopping_list_item, data=item_data, partial=True)
#                 if serializer.is_valid():
#                     serializer.save()
#                 else:
#                     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#             return Response("Shopping list items updated successfully", status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ShoppingList
from .serializers import ShoppingListSerializer

@api_view(['PUT'])
def update_list_items(request):
    if request.method == 'PUT':
        try:
            # Retrieve modified items from request data
            modified_items = request.data  # Assuming modified items are sent directly in request body
            user_id = request.query_params.get('user_id')  # Get user ID from query parameters
            print("User ID:", user_id)

            # Iterate over modified items
            for modified_item in modified_items:
                # Retrieve the ShoppingList instance
                item_id = modified_item.get('id')  # Assuming 'id' is provided in modified items
                print("Item ID:", item_id)
                shopping_list_item = ShoppingList.objects.get(item_id=item_id, user_id=user_id)  # Filter by both item ID and user ID
                print("Shopping List Item:", shopping_list_item)

                # Update the quantity field
                quantity = modified_item.get('quantity')  # Assuming 'quantity' is provided in modified items
                shopping_list_item.quantity = quantity

                # Use serializer to update other fields if needed
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

# from django.views.decorators.http import require_POST
import json
from django.views.decorators.http import require_http_methods


@require_http_methods(["DELETE"])  # Allow only DELETE requests
def delete_list_item(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId')
        user_id = data.get('userId')
        print(item_id)
        print(user_id)

        # Ensure that the item belongs to the authenticated user
        item = ShoppingList.objects.get(item_id=item_id, user_id=user_id)
        print(item)
        item.delete()
        return JsonResponse({'message': 'Item deleted successfully'})
    except ShoppingList.DoesNotExist:
        return JsonResponse({'error': 'Item not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)