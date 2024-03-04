from rest_framework import serializers
from .models import RawFoodPrice

class RawFoodPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawFoodPrice
        fields = '__all__'
