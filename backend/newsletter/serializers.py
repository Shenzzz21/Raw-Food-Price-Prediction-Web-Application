from rest_framework import serializers
from .models import NewsletterMessage


class NewsletterMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterMessage
        fields = '__all__'