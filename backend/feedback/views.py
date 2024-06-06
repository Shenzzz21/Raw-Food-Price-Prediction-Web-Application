from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from .models import Feedback
from django.db.models import Q
from .serializers import FeedbackSerializer
from rest_framework.decorators import api_view
from authentication_app.models import UserAccount

# API endpoint to submit feedback
@api_view(['POST'])
def submit_feedback(request):
    if request.method == 'POST':
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            # Extract user_id from request data
            user_id = request.data.get('user_id')

            # Check if the user exists
            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Save feedback with user_id
            serializer.save(user_id=user_id)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Function to retrieve all feedbacks
def get_feedbacks(request):
    # Retrieve all instances of the Feedback model using the ORM
    feedback_objects = Feedback.objects.all().order_by('-feedback_id')

    # Serialize the queryset into JSON format
    serializer = FeedbackSerializer(feedback_objects, many=True)

    # Return the serialized data as a JSON response
    return JsonResponse(serializer.data, safe=False)


# Function to search for feedbacks based on query parameter
def search_feedbacks(request):
    if request.method == 'GET':
        # Extract the query string from the request
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
                
                # Initialize an empty list to store formatted feedback data
                feedback_data = []
                for feedback in feedbacks:
                    # Format feedback data into a dictionary
                    feedback_info = {
                        'id': feedback.feedback_id,
                        'fullname': feedback.fullname,
                        'email': feedback.email,
                        'feedback_subject': feedback.feedback_subject,
                        'message': feedback.message,
                        # Convert datetime to string
                        'submission_date': feedback.submission_date.strftime('%Y-%m-%d')  
                    }
                    # Append the formatted feedback data to the list
                    feedback_data.append(feedback_info)

                # If feedback_data is empty
                if not feedback_data:  
                    return JsonResponse({'error': 'No feedbacks found'}, status=404)
                return JsonResponse(feedback_data, safe=False)
            
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        
        else:
            return JsonResponse({'error': 'Query parameter "query" is required'}, status=400)
    
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


 # API endpoint to delete a feedback 
@api_view(["DELETE"])
def delete_feedback(request, feedback_id):
    try:
        # Retrieve the feedback object
        feedback = Feedback.objects.get(pk=feedback_id)
        
        # Delete the feedback
        feedback.delete()

        return JsonResponse({'message': 'Feedback deleted successfully'}, status=200)
    except Feedback.DoesNotExist:
        return JsonResponse({'error': 'Feedback not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
