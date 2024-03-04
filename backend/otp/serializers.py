from rest_framework import serializers
from .models import OTP

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['OTP_id', 'email', 'OTP_value', 'expiry_timestamp']
