from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Item
from .serializers import ItemSerializer
from django.shortcuts import get_object_or_404
from django.db import transaction
from raw_food_price.models import RawFoodPrice
from django.core.exceptions import ObjectDoesNotExist
from .models import Category
from django.db.models import Q
from django.db.models import Max, OuterRef, Subquery, F
from decimal import Decimal, InvalidOperation
import pandas as pd
import numpy as np
import pickle
from django.utils import timezone
from datetime import datetime, timedelta
import datetime as dt
import os 
import json

# Define the file paths
data_dir = os.path.join(os.path.dirname(__file__), 'datasets')

# Define the neural network class
class NeuralNetwork:
    def __init__(self, input_nodes, hidden_nodes, output_nodes):
        self.input_nodes = input_nodes
        self.hidden_nodes = hidden_nodes
        self.output_nodes = output_nodes
        self.weights_input_hidden = None
        self.weights_hidden_output = None
        
    def query(self, inputs_list):
        # Check if weights are loaded
        if self.weights_input_hidden is None or self.weights_hidden_output is None:
            raise Exception("Neural network weights are not loaded.")
        
        # Forward pass
        hidden_inputs = np.dot(self.weights_input_hidden, inputs_list)
        hidden_outputs = self.activation_function(hidden_inputs)
        final_inputs = np.dot(self.weights_hidden_output, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)
        
        return final_outputs
    
    @staticmethod
    def activation_function(x):
        return 1 / (1 + np.exp(-x))


# Function to load neural network weights based on the category
def load_neural_network_weights(category):
    try:
        # Construct the file path for the pickle file based on the category
        weights_file_path = os.path.join(os.path.dirname(__file__), 'models', f'neural_network_weights_{category}.pickle')
        
        # Load the trained neural network model from the pickle file
        with open(weights_file_path, 'rb') as file:
            weights_input_hidden = pickle.load(file)
            weights_hidden_output = pickle.load(file)
        
        return weights_input_hidden, weights_hidden_output
    except FileNotFoundError:
        print(f"Neural network weights file not found for category: {category}")
        return None, None
    except Exception as e:
        print(f"Error loading neural network weights for category {category}: {e}")
        return None, None

# Set parameters for the neural network
input_nodes = 1
hidden_nodes = 10
output_nodes = 1


# Function to predict the prices
def predict_price(request):
    if request.method == 'POST':
        try:
            # Parse request data
            data = json.loads(request.body.decode('utf-8'))
            item_name = data.get('item_name')
            category = data.get('category') 

            # Load neural network weights based on the chosen category
            weights_input_hidden, weights_hidden_output = load_neural_network_weights(category) 

            if weights_input_hidden is not None and weights_hidden_output is not None:
                # Create instance of neural network and load weights
                neural_network = NeuralNetwork(input_nodes, hidden_nodes, output_nodes)
                neural_network.weights_input_hidden = weights_input_hidden
                neural_network.weights_hidden_output = weights_hidden_output

                # Load dataset for the specified category
                dataset_path = os.path.join(data_dir, f'{category}.csv')
                dataset = pd.read_csv(dataset_path)
                dataset.dropna(inplace=True)
                if 'Date' in dataset.columns:
                    dataset['Date'] = pd.to_datetime(dataset['Date'], errors='coerce')
                
                # Retrieve data for the specified item and the past two weeks
                if item_name in dataset['Product Name'].unique():
                    item_data = dataset[dataset['Product Name'] == item_name]
                    end_date = dt.datetime.now()
                    start_date = end_date - timedelta(days=14)
                    past_two_weeks_data = item_data[(item_data['Date'] >= start_date) & (item_data['Date'] <= end_date)]
                    
                    if not past_two_weeks_data.empty:
                        # Calculate statistics for the past two weeks
                        past_week_min_price = past_two_weeks_data['Price'].min()
                        past_week_max_price = past_two_weeks_data['Price'].max()
                        past_week_avg_price = past_two_weeks_data['Price'].mean()

                        # Prepare inputs for neural network prediction
                        inputs = past_two_weeks_data['Price'].values.reshape(1, -1) / past_two_weeks_data['Price'].max() * 0.99 + 0.01
                        
                        # Perform prediction using the neural network
                        predicted_price = neural_network.query(inputs)
                        
                        # Check if predicted_price is not None
                        if predicted_price is not None:  
                            predicted_price = predicted_price[0][0] * past_two_weeks_data['Price'].max()
                        else:
                            predicted_price = None

                        # Prepare response data
                        response_data = {
                            'item_name': item_name,
                            'category': category,  
                            'past_week_min_price': past_week_min_price,
                            'past_week_max_price': past_week_max_price,
                            'past_week_avg_price': past_week_avg_price,
                            'predicted_price': predicted_price
                        }

                        return JsonResponse(response_data)
                    else:
                        return JsonResponse({'error': f"No data available for '{item_name}' for the past two weeks ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})."}, status=404)
                else:
                    return JsonResponse({'error': f"Item '{item_name}' not found in the dataset."}, status=404)
            else:
                return JsonResponse({'error': f"Neural network weights are not loaded for category: {category}"}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# Function to update the predictions of items
def update_predictions(request):
    if request.method == 'POST':
        try:
            # # Fetch all items for updating predictions
            # items = Item.objects.all()
            # Fetch all items for updating predictions, excluding items added today
            items = Item.objects.exclude(rawfoodprice__prediction_date=timezone.now().date())
            
            for item in items:
                category_id = item.category_id
                category_name = Category.objects.get(id=category_id).name
                item_name = item.item_name
                print(item_name)

                # Retrieve predicted prices for the item and update database
                response = update_all_prices(item_name, category_name)
                if 'error' not in response:
                    # Update the prices for the item
                    try:
                        # Convert numpy values to native Python types
                        minimum_price = Decimal(float(response.get('past_week_min_price')))
                        maximum_price = Decimal(float(response.get('past_week_max_price')))
                        average_price = Decimal(float(response.get('past_week_avg_price')))
                        predicted_price = Decimal(float(response.get('predicted_price')))
                    except InvalidOperation as e:
                        return JsonResponse({'error': f"Invalid decimal operation: {str(e)}"}, status=400)


                    # Create or update RawFoodPrice entry for the item
                    RawFoodPrice.objects.create(
                        item=item,
                        minimum_price=minimum_price,
                        maximum_price=maximum_price,
                        average_price=average_price,
                        predicted_price=predicted_price,
                        prediction_date=dt.date.today()
                    )
                else:
                    print(f"Error updating predictions for item '{item_name}': {response.get('error')}")

            return JsonResponse({'message': 'Predictions updated successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# Sub Function to update the prices of all items
def update_all_prices(item_name, category):
    try:
        # Load neural network weights based on the chosen category
        weights_input_hidden, weights_hidden_output = load_neural_network_weights(category) 

        if weights_input_hidden is not None and weights_hidden_output is not None:
            # Create instance of neural network and load weights
            neural_network = NeuralNetwork(input_nodes, hidden_nodes, output_nodes)
            neural_network.weights_input_hidden = weights_input_hidden
            neural_network.weights_hidden_output = weights_hidden_output

            # Load dataset for the specified category
            dataset_path = os.path.join(data_dir, f'{category}.csv')  
            dataset = pd.read_csv(dataset_path)
            dataset.dropna(inplace=True)
            if 'Date' in dataset.columns:
                dataset['Date'] = pd.to_datetime(dataset['Date'], errors='coerce')
            
            # Retrieve data for the specified item and the past two weeks
            if item_name in dataset['Product Name'].unique():
                # Calculate statistics for the past two weeks
                item_data = dataset[dataset['Product Name'] == item_name]
                end_date = dt.datetime.now()
                start_date = end_date - timedelta(days=14)
                past_two_weeks_data = item_data[(item_data['Date'] >= start_date) & (item_data['Date'] <= end_date)]
                
                if not past_two_weeks_data.empty:
                    past_week_min_price = past_two_weeks_data['Price'].min()
                    past_week_max_price = past_two_weeks_data['Price'].max()
                    past_week_avg_price = past_two_weeks_data['Price'].mean()

                    # Prepare inputs for neural network prediction
                    inputs = past_two_weeks_data['Price'].values.reshape(1, -1) / past_two_weeks_data['Price'].max() * 0.99 + 0.01
                    
                    # Perform prediction using the neural network                    
                    predicted_price = neural_network.query(inputs)    

                    # Check if predicted_price is not None                
                    if predicted_price is not None:  
                        predicted_price = predicted_price[0][0] * past_two_weeks_data['Price'].max()
                    else:
                        predicted_price = None
                    print('Predicted Price after calculation: ', predicted_price)

                    # Prepare response data
                    response_data = {
                        'item_name': item_name,
                        'category': category,  
                        'past_week_min_price': past_week_min_price,
                        'past_week_max_price': past_week_max_price,
                        'past_week_avg_price': past_week_avg_price,
                        'predicted_price': predicted_price
                    }

                    return response_data
                else:
                    return {'error': f"No data available for '{item_name}' for the past two weeks ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})."}
            else:
                return {'error': f"Item '{item_name}' not found in the dataset."}
        else:
            return {'error': f"Neural network weights are not loaded for category: {category}"}
    except Exception as e:
        return {'error': str(e)}


# Function to add new item to database
@api_view(['POST'])
def add_item(request):
    if request.method == 'POST':
        print('Received data:', request.POST)

        # Fetch the category name from the request data
        category_name = request.data.get('category')

        try:
            # Query the Category model to get the corresponding category object
            category = Category.objects.get(name=category_name)

            # Extract the category ID from the category object
            category_id = category.id

            # Modify the request data to replace category name with category ID
            request.data['category'] = category_id

            # Serialize the data including files
            serializer = ItemSerializer(data=request.data)

            if serializer.is_valid():
                # Use a transaction to ensure data integrity
                with transaction.atomic():
                    # Create the item instance with the category foreign key
                    item_instance = serializer.save(category_id=category_id)

                    # Extract the ID of the newly added item
                    item_id = item_instance.id

                    # Extract other fields from the request data
                    minimum_price = request.data.get('minimum_price')
                    maximum_price = request.data.get('maximum_price')
                    average_price = request.data.get('average_price')
                    predicted_price = request.data.get('predicted_price')

                    # Create a RawFoodPrice instance and save it to the database
                    price_instance = RawFoodPrice.objects.create(
                        item=item_instance,
                        minimum_price=minimum_price,
                        maximum_price=maximum_price,
                        average_price=average_price,
                        predicted_price=predicted_price,
                        prediction_date=dt.date.today()
                    )

                # Return a success response with the serialized data
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Return an error response if serialization fails
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Category.DoesNotExist:
            # Return an error response if the category does not exist
            return Response({'error': f"No Category matches the given query: {category_name}"}, status=status.HTTP_404_NOT_FOUND)


# Function to fetch items from database
def get_items(request):
    try:
        # Subquery to get the latest prediction date for each item
        latest_prediction_subquery = RawFoodPrice.objects.filter(
            item_id=OuterRef('item_id')
        ).order_by('-prediction_date').values('prediction_date')[:1]

        # Query to fetch the items with their latest prediction date
        items = RawFoodPrice.objects.annotate(
            latest_prediction_date=Subquery(latest_prediction_subquery)
        ).filter(
            prediction_date=F('latest_prediction_date')
        ).select_related(
            'item', 'item__category'
        ).order_by('-item__id').values(
            'item__id',
            'item__image',
            'item__item_name',
            'item__category__name',
            'item__quantity',
            'item__unit',
            'minimum_price',
            'average_price',
            'maximum_price',
            'predicted_price',
            'item__calories',
            'item__protein',
            'item__carbohydrate',
            'item__fat',
            'item__iron',
            'item__sugar',
            'prediction_date'
        )

        # Convert the queryset to a list of dictionaries with the specified names
        items_list = []
        for item in items:
            item_info = {
                'id': item['item__id'],
                'image': item['item__image'],
                'item_name': item['item__item_name'],
                'category_name': item['item__category__name'],
                'item__quantity': f"{item['item__quantity']} {item['item__unit']}",
                'minimum_price': item['minimum_price'],
                'average_price': item['average_price'],
                'maximum_price': item['maximum_price'],
                'predicted_price': item['predicted_price'],
                'calories': f"{item['item__calories']}",
                'protein': f"{item['item__protein']}",
                'carbohydrate': f"{item['item__carbohydrate']}",
                'fat': f"{item['item__fat']}",
                'iron': f"{item['item__iron']}",
                'sugar': f"{item['item__sugar']}",
                'prediction_date': item['prediction_date']
            }
            items_list.append(item_info)

        # Return the fetched item data as a JSON response
        return JsonResponse(items_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Function to get the item data for prediciton page
def prediction_page_items(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category_name = data.get('category', '')
        
        try:
            # Fetch the category object from the Category model
            category = Category.objects.get(name=category_name)
            
            # Get the most recent prediction date for each distinct item
            latest_prediction_dates = RawFoodPrice.objects.values('item_id').annotate(latest_prediction_date=Max('prediction_date'))

            # Fetch items related to the specified category along with their most recent price data
            items = []
            for item_data in latest_prediction_dates:
                latest_prediction_date = item_data['latest_prediction_date']
                item_id = item_data['item_id']
                item_price_data = RawFoodPrice.objects.filter(prediction_date=latest_prediction_date, item_id=item_id).first()
                if item_price_data and item_price_data.item.category == category:
                    items.append({
                        'item_id': item_id,
                        'item__image': item_price_data.item.image.url if item_price_data.item.image else None,
                        'item__item_name': item_price_data.item.item_name,
                        'item__quantity': item_price_data.item.quantity,
                        'item__unit': item_price_data.item.unit,
                        'minimum_price': item_price_data.minimum_price,
                        'maximum_price': item_price_data.maximum_price,
                        'average_price': item_price_data.average_price,
                        'predicted_price': item_price_data.predicted_price
                    })

            return JsonResponse(items, safe=False)
        
        except Category.DoesNotExist:
            return JsonResponse({'error': 'Category not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


# Function to fetch data for nutritional info page
def get_item_data(request, item_id):
    try:
        # Retrieve the item object from the database or return a 404 error if not found
        item = get_object_or_404(Item, id=item_id)
        # Retrieve the latest price data for the item
        price_data = RawFoodPrice.objects.filter(item_id=item_id).order_by('-prediction_date').first() 
        
        # Construct a dictionary containing item data
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
            'minimum_price': price_data.minimum_price if price_data else None,
            'maximum_price': price_data.maximum_price if price_data else None,
            'average_price': price_data.average_price if price_data else None,
            'predicted_price': price_data.predicted_price if price_data else None,
        }
        print(item_data)
        return JsonResponse(item_data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Function to fetch items according to category
def get_items_by_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('category')
            if category_name is not None:
                # Fetch the category object from the Category model
                try:
                    category = Category.objects.get(name=category_name)
                except Category.DoesNotExist:
                    return JsonResponse({'error': 'Category not found'}, status=404)
                
                # Fetch items related to the specified category along with their price data
                items = Item.objects.filter(category=category).values()
                items_with_prices = []
                for item in items:
                    raw_food_price = RawFoodPrice.objects.filter(item_id=item['id']).first()
                    if raw_food_price:
                        # Include both item and price data in a single dictionary
                        item_with_price = {
                            'id': item['id'],
                            'item_name': item['item_name'],
                            'category': category_name,
                            'quantity': item['quantity'],
                            'unit': item['unit'],
                            'calories': item['calories'],
                            'protein': item['protein'],
                            'carbohydrate': item['carbohydrate'],
                            'fat': item['fat'],
                            'iron': item['iron'],
                            'sugar': item['sugar'],
                            'image': item['image'],
                            'minimum_price': raw_food_price.minimum_price,
                            'maximum_price': raw_food_price.maximum_price,
                            'average_price': raw_food_price.average_price,
                            'predicted_price': raw_food_price.predicted_price
                        }
                    else:
                        # If price data not available, include None for prices
                        item_with_price = {
                            'id': item['id'],
                            'item_name': item['item_name'],
                            'category': category_name,
                            'quantity': item['quantity'],
                            'unit': item['unit'],
                            'calories': item['calories'],
                            'protein': item['protein'],
                            'carbohydrate': item['carbohydrate'],
                            'fat': item['fat'],
                            'iron': item['iron'],
                            'sugar': item['sugar'],
                            'image': item['image'],
                            'minimum_price': None,
                            'maximum_price': None,
                            'average_price': None,
                            'predicted_price': None
                        }
                    items_with_prices.append(item_with_price)

                return JsonResponse({'items': items_with_prices}, safe=False)
            else:
                return JsonResponse({'error': 'Category not provided'}, status=400)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# Function to get data for time series grapg
def get_data_time_series(request, item_id):
    try:
        # Ensure the item exists
        item = get_object_or_404(Item, id=item_id)
        
        # Query price data for the item ordered by prediction date
        price_data = RawFoodPrice.objects.filter(item_id=item_id).order_by('prediction_date')
        
        # Serialize price data into JSON format
        time_series = [{
            # Convert date to string format
            'date': data.prediction_date.strftime('%Y-%m-%d'),  
            'average_price': data.average_price,
            'predicted_price': data.predicted_price
        } for data in price_data]

        # Return JSON response with time series data
        return JsonResponse(time_series, safe=False)
    except Exception as e:
        # Return error response in case of any exceptions
        return JsonResponse({'error': str(e)}, status=500)


# Function for searching items in search bar
def search_items(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            try:
                # Perform case-insensitive partial match search on item_name field
                items = Item.objects.filter(Q(item_name__icontains=query)).distinct()
                
                item_data = []
                
                # Search in items
                for item in items:
                    # Check if the category ID in Item table matches Category table
                    if item.category_id is not None:
                        category = Category.objects.filter(id=item.category_id).first()
                        if category:
                            category_name = category.name
                        else:
                            category_name = None
                    else:
                        category_name = None

                    item_info = {
                        'item_id': item.id,
                        'image': item.image.url if item.image else None,
                        'item_name': item.item_name,
                        'category_name': category_name,
                        'item__quantity': f"{item.quantity} {item.unit}",
                        'calories': item.calories,
                        'protein': item.protein,
                        'carbohydrate': item.carbohydrate,
                        'fat': item.fat,
                        'iron': item.iron,
                        'sugar': item.sugar,
                    }
                    
                    # Fetch predicted price from RawFoodPrice model
                    try:
                        price_data = RawFoodPrice.objects.filter(item=item)
                        latest_price = price_data.latest('prediction_date')
                        item_info.update({
                            'minimum_price': latest_price.minimum_price,
                            'average_price': latest_price.average_price,
                            'maximum_price': latest_price.maximum_price,
                            'predicted_price': latest_price.predicted_price,
                        })
                    except RawFoodPrice.DoesNotExist:
                        item_info.update({
                            'minimum_price': None,
                            'average_price': None,
                            'maximum_price': None,
                            'predicted_price': None,
                        })
                    
                    item_data.append(item_info)
                
                if not item_data:
                    return JsonResponse({'error': 'Item not found'}, status=404)
                
                return JsonResponse(item_data, safe=False)
            
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        else:
            return JsonResponse({'error': 'Query parameter "query" is required'}, status=400)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# Function to update details of an item
@api_view(['PUT'])
def update_item(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            item_data = data.get('item')
            
            if item_data:
                item_id = item_data.get('id')
                
                if item_id:
                    try:
                        # Retrieve the item and its price data from the database
                        item = Item.objects.get(pk=item_id)
                        # Retrieve the latest price data based on the prediction date
                        price = RawFoodPrice.objects.filter(item_id=item_id).order_by('-prediction_date').first()
                        
                        # Update item details based on the provided data
                        if 'item_name' in item_data:
                            item.item_name = item_data['item_name']
                        if 'category' in item_data:
                            category_id = item_data['category']
                            item.category_id = category_id         

                        if 'quantity' in item_data:
                            quantity = item_data['quantity']
                            unit = None

                            # Separate numeric value from unit
                            if quantity and isinstance(quantity, str):
                                numeric_quantity = ''.join(filter(str.isdigit, quantity))
                                unit = ''.join(filter(str.isalpha, quantity))

                                # Convert numeric quantity to float
                                quantity = float(numeric_quantity) / 100 if numeric_quantity else None
                                # dividing by 100 because the numeric value might be 100.00, 
                                # and we want to store 100.00 as 100.00 in the database                        
                            item.quantity = quantity
                            item.unit = unit

                        # Update price data if provided
                        if 'minimumPrice' in item_data:
                            price.minimum_price = item_data['minimumPrice']
                        if 'averagePrice' in item_data:
                            price.average_price = item_data['averagePrice']
                        if 'maximumPrice' in item_data:
                            price.maximum_price = item_data['maximumPrice']
                        if 'predictedPrice' in item_data:
                            price.predicted_price = item_data['predictedPrice']
                        if 'calories' in item_data:
                            item.calories = item_data['calories']
                        if 'protein' in item_data:
                            item.protein = item_data['protein']
                        if 'carbohydrate' in item_data:
                            item.carbohydrate = item_data['carbohydrate']
                        if 'fat' in item_data:
                            item.fat = item_data['fat']
                        if 'iron' in item_data:
                            item.iron = item_data['iron']
                        if 'sugar' in item_data:
                            item.sugar = item_data['sugar']
                        
                        # Save the updated item and price
                        item.save()
                        price.save()
                        
                        return JsonResponse({'message': 'Item updated successfully'}, status=200)
                    except ObjectDoesNotExist:
                        return JsonResponse({'error': 'Item or price not found'}, status=404)
                else:
                    return JsonResponse({'error': 'Item ID is required'}, status=400)
            else:
                return JsonResponse({'error': 'Item data is missing'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# Function to delete details of an item
@api_view(['DELETE'])
def delete_item(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            itemId = data['itemId']

            # Retrieve the item from the database and delete it
            item = Item.objects.get(pk=itemId)
            item.delete()

            # Also delete related data from RawFoodPrice table
            RawFoodPrice.objects.filter(item_id=itemId).delete()

            return JsonResponse({'message': 'Item deleted successfully'}, status=200)
        except Item.DoesNotExist:
            return JsonResponse({'error': 'Item does not exist'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)