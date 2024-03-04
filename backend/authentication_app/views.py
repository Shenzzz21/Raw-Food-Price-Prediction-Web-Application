# # views.py

# from rest_framework import generics
# from .models import UserAccount
# from .serializers import UserCreateSerializer

# class UserListAPIView(generics.ListAPIView):
#     queryset = UserAccount.objects.all()
#     serializer_class = UserCreateSerializer

# views.py

from django.db import connection
from django.http import JsonResponse

# authentication_app/views.py

# import axios
from django.contrib.auth import authenticate

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        # user = authenticate(request, email=email, password=password)
        # if user is not None:
        #     # Check if the email matches the specific email and redirect to dashboard
        #     if email == 'sheneeza.chaudhary@gmail.com':
        #         return JsonResponse({'redirect': '/dashboard'})
        #     else:
        #         # Handle other authenticated users, e.g., redirect to home page
        #         return JsonResponse({'redirect': '/home'})
        # else:
        #     # Handle invalid credentials
        #     return JsonResponse({'error': 'Invalid email or password'}, status=400)
    else:
        # Handle invalid request method
        return JsonResponse({'error': 'Invalid request method'}, status=405)



def get_users(request):
    # Execute SQL query to fetch user data
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name, email, registered_date, subscription_status, subscription_date FROM public.authentication_app_useraccount ORDER BY id DESC")
        rows = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries
    users = []
    for row in rows:
        user = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'registered_date': row[3],
            'subscription_status': row[4],
            'subscription_date': row[5],
            # Add other fields as needed
        }
        users.append(user)

    # Return the fetched user data as JSON response
    return JsonResponse(users, safe=False)


from django.db.models import Q
from .models import UserAccount  # Assuming you have a User model

def search_users(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            # Perform the search using case-insensitive match on user's name or email
            results = UserAccount.objects.filter(Q(name__icontains=query) | Q(email__icontains=query))
            # Serialize the results if needed
            serialized_results = [{'name': user.name, 'email': user.email, 'registered_date': user.registered_date,
                                   'subscription_status': user.subscription_status, 'subscription_date': user.subscription_date}
                                  for user in results]
            return JsonResponse(serialized_results, safe=False)
        else:
            return JsonResponse({'error': 'No search query provided'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    


from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import UserAccount
import json

# @require_POST
@api_view(['PUT'])
def update_user(request):
        if request.method == 'PUT':
            try:
                data = json.loads(request.body)
                user_data = data.get('user')
                print(user_data)
                if user_data:
                    user_id = user_data.get('id')
                    print(user_id)
                    if user_id:
                        user = UserAccount.objects.get(pk=user_id)
                        # Update user details
                        user.name = user_data.get('name')
                        user.email = user_data.get('email')
                        # Save the updated user
                        user.save()
                        return JsonResponse({'message': 'User updated successfully'}, status=200)
                    else:
                        return JsonResponse({'error': 'User ID is required'}, status=400)
                else:
                    return JsonResponse({'error': 'User data is missing'}, status=400)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserAccount

@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    try:
        # Retrieve the user object
        user = UserAccount.objects.get(pk=user_id)
        
        # Delete the user
        user.delete()
        
        return JsonResponse({'message': 'User deleted successfully'}, status=200)
    except UserAccount.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





@api_view(['GET'])
def user_details(request):
    if request.method == 'GET':
        try:
            user_id = request.user.id  # Get the current user's id
            user = UserAccount.objects.get(pk=user_id)
            # Extract user details
            user_details = {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
            return JsonResponse(user_details, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def update_profile(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_id = data.get('userId')  # Extract userId from request data
            if user_id:
                user = UserAccount.objects.get(pk=user_id)
                # Update user details
                user.name = data.get('name')
                user.email = data.get('email')
                # Save the updated user
                user.save()
                return JsonResponse({'message': 'Profile updated successfully'}, status=200)
            else:
                return JsonResponse({'error': 'User ID is required'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)