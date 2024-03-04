from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from . models import NewsletterMessage, UserNewsletter
from django.utils import timezone
# from django_pandas.io import read_frame
import pandas as pd
from .models import UserAccount
import json
from django.db import connection
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['POST'])
def subscribe_newsletter(request):
    if request.method == 'POST':
        # Get email and userId from the request
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        userId = data.get('userId')

        subject = 'Welcome to our Newsletter!'
        message = 'Thank you for subscribing to our newsletter. We will keep you updated with the latest news and updates.'
    
        # Check if the user exists
        try:
            user = UserAccount.objects.get(id=userId)
        except UserAccount.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the provided email matches the user's email
        if email == user.email:
            if user.subscription_status:
                # User is already subscribed
                return JsonResponse({'message': 'User is already subscribed'}, status=200)
            else:
                send_mail(
                    subject,
                    message,
                    '',
                    [email],
                    fail_silently=False,
                )
                # Update subscription status and subscription date
                user.subscription_status = True
                user.subscription_date = timezone.now()
                user.save()
                return JsonResponse({'message': 'Subscription successful'}, status=200)
        else:
            return JsonResponse({'error': 'Email does not match user'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_subscribers(request):
    # Execute SQL query to fetch subscriber data
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, subscription_date FROM public.authentication_app_useraccount WHERE subscription_status = True ORDER BY subscription_date DESC")
        rows = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries
    subscribers = []
    for row in rows:
        subscriber = {
            'email': row[0],
            'subscription_date': row[1],
            # Add other fields as needed
        }
        subscribers.append(subscriber)

    # Return the fetched subscriber data as JSON response
    return JsonResponse(subscribers, safe=False)

@api_view(['POST'])
def send_newsletter(request):
    if request.method == 'POST':
        data = request.data
        subject = data.get('subject')
        message = data.get('message')
        print('Subject: ', subject)
        print('Message: ', message)

        try:
            # Save the newsletter message to the database
            newsletter = NewsletterMessage.objects.create(subject=subject, message=message)

            # Fetch subscribers from the database
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, email FROM public.authentication_app_useraccount WHERE subscription_status = True ORDER BY id ASC")
                subscribers = cursor.fetchall()

                print(subscribers)

                df = pd.DataFrame(subscribers, columns=['id', 'email'])
                # Extract user IDs as a list
                subscriber_ids = df['id'].values.tolist()
                # Extract email addresses as a list
                subscriber_emails = df['email'].values.tolist()

                print(subscriber_ids)
                print(subscriber_emails)

                send_mail(
                    subject,
                    message,
                    '',
                    subscriber_emails,
                    fail_silently=False,
                )

                # Insert data into the bridge table associating user IDs with the newsletter ID
                for subscriber_id in subscriber_ids:
                    # Fetch UserAccount instance corresponding to the subscriber_id
                    user = UserAccount.objects.get(id=subscriber_id)
                    # Create UserNewsletter entry
                    bridge_entry = UserNewsletter.objects.create(newsletter=newsletter, user=user)


            return Response({'message': 'Newsletter sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# def get_newsletters(request):
#     # Execute SQL query to fetch newseltter data
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT subject, message, sent_date FROM public.newsletter_newslettermessage ORDER BY id DESC")
#         rows = cursor.fetchall()

#     # Convert the fetched data into a list of dictionaries
#     newsletters = []
#     for row in rows:
#         newsletter = {
#             'subject': row[0],
#             'message': row[1],
#             'sent_date': row[2],
#         }
#         newsletters.append(newsletter)

#     # Return the fetched newsletter data as JSON response
#     return JsonResponse(newsletters, safe=False)
        

def get_newsletters(request):
    # Fetch newsletter data from the database
    newsletters = NewsletterMessage.objects.values('subject', 'message', 'sent_date').order_by('-id')

    # Convert queryset to list of dictionaries
    newsletters_data = list(newsletters)

    # Return the fetched newsletter data as JSON response
    return JsonResponse(newsletters_data, safe=False)