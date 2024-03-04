from rest_framework import serializers
from .models import NewsletterMessage

# class NewsletterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Newsletter
#         fields = ['newsletter_id', 'email', 'newsletter_subject', 'newsletter_message', 'sent_date']

# class SubscribersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subscribers
#         fields = '__all__'

class NewsletterMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterMessage
        fields = '__all__'