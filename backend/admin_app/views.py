from django.http import JsonResponse
from authentication_app.models import UserAccount
from raw_food_item.models import Item, Category
from raw_food_price.models import RawFoodPrice
from feedback.models import Feedback
from django.db.models import Count, Max, Subquery
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view

# Function to fetch data for the dashboard
def dashboard_data(request):
    # Count total users, items, feedbacks, and subscribers
    total_users = UserAccount.objects.count()
    total_items = Item.objects.count()
    total_feedbacks = Feedback.objects.count()
    # Count the number of users with subscription_status as true
    total_subscribers = UserAccount.objects.filter(subscription_status=True).count()

    # Prepare data for the dashboard
    data = {
        'total_users': total_users,
        'total_items': total_items,
        'total_feedbacks': total_feedbacks,
        'total_subscribers': total_subscribers
    }

    return JsonResponse(data)


# Function to fetch data for the doughnut chart
def doughnut_chart_data(request):
    # Count subscribed and not subscribed users
    subscribed_users = UserAccount.objects.filter(subscription_status=True).count()
    not_subscribed_users = UserAccount.objects.filter(subscription_status=False).count()

    # Prepare data for the doughnut chart
    data = {
        'subscribed_users': subscribed_users,
        'not_subscribed_users': not_subscribed_users,
    }

    return JsonResponse(data)


# Function to fetch data for the bar chart
def bar_chart_data(request):
    # Get distinct categories and count items in each category
    category_counts = Category.objects.annotate(count=Count('item'))

    # Format data for the chart
    labels = [category.name for category in category_counts]
    data = [category.count for category in category_counts]

    # Prepare response data
    chart_data = {
        'labels': labels,
        'data': data
    }

    return JsonResponse(chart_data)


# API endpoint to fetch data for expensive items
@api_view(['GET'])
def expensive_items_data(request):
    expensive_items = []
    try:
        # Get distinct categories for items
        categories = RawFoodPrice.objects.values_list('item__category', flat=True).distinct()
        
        # Iterate over each category to find the most expensive item
        for category_id in categories:
            # Retrieve category object
            category = Category.objects.get(id=category_id)
            # Find the most expensive item in the category
            item = RawFoodPrice.objects.filter(item__category=category_id).order_by('-maximum_price').first()
            
            # If the item exists, add its details to the list of expensive items
            if item:
                expensive_items.append({
                    'category': category.name,
                    'image': item.item.image.url if item.item.image else None,
                    'item_name': item.item.item_name,
                    'maximum_price': item.maximum_price,
                })
    except ObjectDoesNotExist:
        # Ignore cases where the object does not exist
        pass  
    return Response(expensive_items)


# API endpoint to fetch data for cheap items
@api_view(['GET'])
def cheap_items_data(request):
    cheap_items = []
    try:
        # Get distinct categories for items
        categories = RawFoodPrice.objects.values_list('item__category', flat=True).distinct()
        
        # Iterate over each category to find the cheapest item
        for category_id in categories:
            # Retrieve category object
            category = Category.objects.get(id=category_id)
            # Find the cheapest item in the category
            item = RawFoodPrice.objects.filter(item__category=category_id).order_by('minimum_price').first()
            
            # If the item exists, add its details to the list of cheap items
            if item:
                cheap_items.append({
                    'category': category.name,
                    'image': item.item.image.url if item.item.image else None,
                    'item_name': item.item.item_name,
                    'minimum_price': item.minimum_price,
                })
    except ObjectDoesNotExist:
        # Ignore cases where the object does not exist
        pass  
    return Response(cheap_items)


# Function to fetch data for the price distribution chart
def price_distribution_data(request):
    # Subquery to get the maximum prediction date for each item
    latest_dates_subquery = RawFoodPrice.objects.values('item_id').annotate(max_prediction_date=Max('prediction_date')).values('item_id', 'max_prediction_date')

    # Query to filter records based on the latest prediction date for each item
    latest_prices = RawFoodPrice.objects.filter(prediction_date__in=Subquery(latest_dates_subquery.values('max_prediction_date')))

    # Aggregate the data by average_price
    price_distribution = latest_prices.values('average_price').annotate(count=Count('id')).order_by('average_price')

    labels = [entry['average_price'] for entry in price_distribution]
    data = [entry['count'] for entry in price_distribution]

    # Prepare data for the price distribution chart
    return JsonResponse({
        'labels': labels,
        'datasets': [{
            'label': 'Price Distribution',
            'data': data,
        }]
    })