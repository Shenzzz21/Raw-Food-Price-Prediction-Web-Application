from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        extra_kwargs = {
            # This ensures the image field is required
            'image': {'required': True},  
        }

    def create(self, validated_data):
        # Extract and remove the 'image' field from the validated data
        image_file = validated_data.pop('image', None)
        # Create a new Item instance using the remaining validated data
        item = Item.objects.create(**validated_data)
        # If an image was provided, save it to the 'image' field of the item
        if image_file:
            item.image = image_file
            item.save()
        return item