from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from . models import NewsletterMessage, UserNewsletter
from django.utils import timezone
from .models import UserAccount
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import redirect
import json

# Function for subscribing to newsletter
@api_view(['POST'])
def subscribe_newsletter(request):
    if request.method == 'POST':
        # Get email and userId from the request
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email')
        userId = data.get('userId')

        # Define email subject and message
        subject = 'Welcome to our Newsletter!'
        message = '''Dear subscriber, we are pleased to welcome you to our community to share our latest news and updates with you. 
Stay tuned for exciting announcements!
        
Kind regards,
AgroCost'''
    
        # Check if the user exists
        try:
            user = UserAccount.objects.get(id=userId)
        except UserAccount.DoesNotExist:
            # Return error response if user is not found
            return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the provided email matches the user's email
        if email == user.email:
            if user.subscription_status:
                # Return message if user is already subscribed
                return JsonResponse({'message': 'User is already subscribed'}, status=200)
            else:
                # Send welcome email and update subscription status and date
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
            # Return error response if email does not match user
            return JsonResponse({'error': 'Email does not match user'}, status=400)

    # Return error response if method is not allowed
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Function to get all subscribers
def get_subscribers(request):
    # Fetch subscribers from the database using Django ORM
    subscribers = UserAccount.objects.filter(subscription_status=True).order_by('-subscription_date')

    # Convert queryset to list of dictionaries
    subscribers_data = []
    for subscriber in subscribers:
        subscriber_info = {
            'email': subscriber.email,
            'subscription_date': subscriber.subscription_date,
        }
        subscribers_data.append(subscriber_info)

    # Return fetched subscriber data as JSON response
    return JsonResponse(subscribers_data, safe=False)


# Function to send newsletters to subscribers
@api_view(['POST'])
def send_newsletter(request):
    if request.method == 'POST':
        # Get subject and message from request data
        data = request.data
        subject = data.get('subject')
        message = data.get('message')

        try:
            # Save the newsletter message to the database
            newsletter = NewsletterMessage.objects.create(subject=subject, message=message)

            # Fetch subscribers from the database
            subscribers = UserAccount.objects.filter(subscription_status=True).order_by('id')

            for subscriber in subscribers:
                # Generate unique token for each subscriber
                token = default_token_generator.make_token(subscriber)
                # Encode the user ID and token for the unsubscribe link
                uidb64 = urlsafe_base64_encode(force_bytes(subscriber.id))
                unsubscribe_link = f'http://localhost:8000/newsletter/unsubscribe/{uidb64}/{token}/'
                
                # Append the unsubscribe link to the message body
                message_with_unsubscribe_link = f"{message}\n\nKind regards,\nAgroCost\n\n\nTo unsubscribe from further newsletters, click the following link:\n{unsubscribe_link}"

                # Send the email
                send_mail(
                    subject,
                    message_with_unsubscribe_link,
                    '',
                    [subscriber.email],
                    fail_silently=False,
                )

                # Insert data into the bridge table associating user IDs with the newsletter ID
                bridge_entry = UserNewsletter.objects.create(newsletter=newsletter, user=subscriber)

            return Response({'message': 'Newsletter sent successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Function to unsubscribe from the newsletter
def unsubscribe(request, uidb64, token):
    try:
        # Decode user ID and retrieve user
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserAccount.objects.get(pk=uid)
        # Check token validity
        if default_token_generator.check_token(user, token):
            user.subscription_status = False
            user.subscription_date = None
            user.save()
            # Redirect to the confirmation page URL
            return redirect('/unsubscribe/confirmation/')
        else:
            # Return error response if token is invalid
            return JsonResponse({'error': 'Invalid token.'}, status=400)
    except (TypeError, ValueError, OverflowError, UserAccount.DoesNotExist):
        # Return error response if an exception occurs
        return JsonResponse({'error': 'Invalid user ID.'}, status=400)


# Function to get all sent newsletters
def get_newsletters(request):
    # Fetch newsletter data from the database
    newsletters = NewsletterMessage.objects.values('subject', 'message', 'sent_date').order_by('-id')

    # Convert queryset to list of dictionaries
    newsletters_data = list(newsletters)

    # Return the fetched newsletter data as JSON response
    return JsonResponse(newsletters_data, safe=False)