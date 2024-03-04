from django.db import models
from raw_food_item.models import Item

class RawFoodPrice(models.Model):
    id = models.AutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    prediction_date = models.DateField()
 