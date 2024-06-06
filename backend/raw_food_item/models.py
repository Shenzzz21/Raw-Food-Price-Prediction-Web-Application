from django.db import models
from category.models import Category

class Item(models.Model):

    # Choices for the 'unit' field
    UNIT_CHOICES = [
        ('kg', 'kg'),
        ('gm', 'gm'),
        ('ltr', 'ltr'),
        ('ml', 'ml'),
        ('dozen', 'dozen'),
        ('pieces', 'pieces'),
        ('pellets', 'pellets'),
        ('bunch', 'bunch'),
    ]

    # Fields for the Item model
    item_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, choices=UNIT_CHOICES)
    calories = models.DecimalField(max_digits=10, decimal_places=2)
    protein = models.DecimalField(max_digits=10, decimal_places=2)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2)
    iron = models.DecimalField(max_digits=10, decimal_places=2)
    sugar = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(null=True, blank=True, upload_to='items/')

    def __str__(self):
        return self.item_name
