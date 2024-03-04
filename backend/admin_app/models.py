from django.db import models

class Item(models.Model):
    CATEGORY_CHOICES = [
        # first value is the one to store in database
        # second value is the one that is displayed to user to choose from
        ('Dairy', 'Dairy'),
        ('Dry Fruits', 'Dry Fruits'),
        ('Eggs', 'Eggs'),
        ('Flour', 'Flour'),
        ('Fruits', 'Fruits'),
        ('Meat', 'Meat'),
        ('Oil', 'Oil'),
        ('Pulses', 'Pulses'),
        ('Rice', 'Rice'),
        ('Salt', 'Salt'),
        ('Spices', 'Spices'),
        ('Vegetables', 'Vegetables'),
    ]

    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('gm', 'gm'),
        ('ltr', 'ltr'),
        ('ml', 'ml'),
    ]

    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)
    minimum_price = models.DecimalField(max_digits=10, decimal_places=2)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=2)
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    calories = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    iron = models.DecimalField(max_digits=10, decimal_places=2)
    sugar = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='items/', null=True, blank=True)

    def __str__(self):
        return self.item_name
