from django.db import models
from authentication_app.models import UserAccount
from django.utils import timezone

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    # email = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)  # Updated: fullname field is nullable
    email = models.EmailField(max_length=255, null=True)
    feedback_subject = models.CharField(max_length=255)
    message = models.TextField()
    submission_date = models.DateField(auto_now_add=True)  # Set to current date on object creation
