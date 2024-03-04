# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Feedback
# from .serializers import FeedbackSerializer
# from authentication_app.models import UserAccount  # Import the UserAccount model
# from django.views.decorators.csrf import csrf_exempt
# from django.db.models import Q
# from django.db import connection



# @api_view(['POST'])
# def submit_feedback(request):
#     if request.method == 'POST':
#         serializer = FeedbackSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # @api_view(['POST'])
# # def submit_feedback(request):
# #     if request.method == 'POST':
# #         serializer = FeedbackSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         else:
# #             print("Validation Error:", serializer.errors)  # Log the serializer errors
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @csrf_exempt
# @api_view(['POST'])
# def submit_feedback(request):
#     if request.method == 'POST':
#         serializer = FeedbackSerializer(data=request.data)
#         if serializer.is_valid():
#             # Check if the email matches any user in the UserAccount model
#             email = serializer.validated_data['email']
#             user = UserAccount.objects.filter(email=email).first()
#             if user:
#                 # If a user with the provided email exists, get the user ID
#                 user_id = user.id
#                 # Save the feedback with the user ID
#                 serializer.save(email=user_id)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             else:
#                 # If no user with the provided email exists, return a validation error
#                 return Response({'email': ['User with this email does not exist.']}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             print("Validation Error:", serializer.errors)  # Log the serializer errors
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @csrf_exempt
# @api_view(['GET'])
# def get_user_id(request):
#     if request.method == 'GET':
#         email = request.query_params.get('email', None)
#         if email:
#             try:
#                 # Execute SQL query to retrieve the user ID based on email
#                 with connection.cursor() as cursor:
#                     cursor.execute("SELECT id FROM public.authentication_app_useraccount WHERE email = %s", [email])
#                     row = cursor.fetchone()
#                     if row:
#                         # If a user with the provided email exists, return the user ID
#                         user_id = row[0]
#                         return Response({'id': user_id}, status=status.HTTP_200_OK)
#                     else:
#                         # If no user found with the email, return a not found response
#                         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#             except Exception as e:
#                 # Handle any exceptions that might occur during query execution
#                 return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             # If no email provided, return a bad request response
#             return Response({'error': 'Email parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .models import Feedback
from .serializers import FeedbackSerializer
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from authentication_app.models import UserAccount
from django.db import connection

@csrf_exempt
@api_view(['POST'])
def submit_feedback(request):
    if request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            # Extract user_id from request data
            user_id = request.data.get('user_id')
            print(user_id)

            # Check if the user exists
            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Save feedback with user_id
            serializer.save(user_id=user_id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_feedbacks(request):
    # Execute SQL query to fetch feedback data
    with connection.cursor() as cursor:
        cursor.execute("SELECT feedback_id, fullname, email, feedback_subject, message, submission_date FROM public.feedback_feedback ORDER BY feedback_id DESC")
        rows = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries
    feedbacks = []
    for row in rows:
        feedback = {
            'feedback_id': row[0],
            'fullname': row[1],
            'email': row[2],
            'feedback_subject': row[3],
            'message': row[4],
            'submission_date': row[5],
            # Add other fields as needed
        }
        feedbacks.append(feedback)

    # Return the fetched user data as JSON response
    return JsonResponse(feedbacks, safe=False)


from django.http import JsonResponse
from .models import Feedback
from django.db.models import Q

def search_feedbacks(request):
    if request.method == 'GET':
        query = request.GET.get('query')
        if query:
            try:
                # Perform case-insensitive partial match search on multiple fields
                feedbacks = Feedback.objects.filter(
                    Q(fullname__icontains=query) |
                    Q(email__icontains=query) |
                    Q(feedback_subject__icontains=query) |
                    Q(message__icontains=query)
                )
                
                feedback_data = []
                for feedback in feedbacks:
                    feedback_info = {
                        'id': feedback.feedback_id,
                        'fullname': feedback.fullname,
                        'email': feedback.email,
                        'feedback_subject': feedback.feedback_subject,
                        'message': feedback.message,
                        'submission_date': feedback.submission_date.strftime('%Y-%m-%d')  # Convert datetime to string
                    }
                    feedback_data.append(feedback_info)
                    
                if not feedback_data:  # If feedback_data is empty
                    return JsonResponse({'error': 'No feedbacks found'}, status=404)
                return JsonResponse(feedback_data, safe=False)
            
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        else:
            return JsonResponse({'error': 'Query parameter "query" is required'}, status=400)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
