from django.http import JsonResponse
from django.db.models import Q
from .models import UserAccount
from rest_framework.decorators import api_view
from django.core.mail import send_mail
import json

# Function to check if a user is an admin
@api_view(['POST'])
def check_is_admin(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        if email:
            # Fetch user details by email
            user = UserAccount.objects.get(email=email)
            # Check if the user is a superuser
            is_superuser = user.is_superuser
            print(user)
            return JsonResponse({'is_superuser': is_superuser})
        else:
            return JsonResponse({'error': 'Email is required'}, status=400)
    except UserAccount.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

# Function to get all users   
def get_users(request):
    # Fetch user data
    users = UserAccount.objects.all().values('id', 'name', 'email', 'registered_date', 'is_active', 'subscription_status', 'subscription_date')
    return JsonResponse(list(users), safe=False)


# Function to search for users by name or email
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
    

# Function to update user details
@api_view(['PUT'])
def update_user(request):
        if request.method == 'PUT':
            try:
                data = json.loads(request.body)
                user_data = data.get('user')

                if user_data:
                    user_id = user_data.get('id')

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

# Function to delete a user
@api_view(["DELETE"])
def delete_user(request, user_id):
    try:
        # Retrieve the user object
        user = UserAccount.objects.get(pk=user_id)
        # Fetch user's email and username
        user_email = user.email
        username = user.name
        # Delete the user
        user.delete()
        # Send email to the user
        send_mail(
            'Important: Account Deletion Notification',
            f"Dear {username},\n\nWe regret to inform you that your account with the username '{username}' on AgroCost has been deleted. This action was taken in accordance with our policies and procedures.\n\nWe understand that this may come as a surprise, and we want to assure you that this decision was not made lightly. If you have any questions or concerns regarding the deletion of your account, please do not hesitate to reach out to our support team.\n\nWe apologize for any inconvenience this may cause you.\n\nThank you for your understanding.",
            'from@example.com',
            [user_email],
            fail_silently=False,
        )
        return JsonResponse({'message': 'User deleted successfully'}, status=200)
    except UserAccount.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Function to get details of the logged-in user
@api_view(['GET'])
def user_details(request):
    if request.method == 'GET':
        try:
            # Get the current user's id
            user_id = request.user.id  
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


# Function to update the profile of the logged-in user
def update_profile(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            # Extract userId from request data
            user_id = data.get('userId')  
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