from django.db import models
from authentication_app.models import UserAccount
from raw_food_item.models import Item

class ShoppingList(models.Model):
    list_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    item_active = models.BooleanField(default=True)  # Added boolean field
    # subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateField(auto_now_add=True)
