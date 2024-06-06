from rest_framework import serializers
from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['feedback_id', 'fullname', 'email', 'feedback_subject', 'message', 'submission_date']
