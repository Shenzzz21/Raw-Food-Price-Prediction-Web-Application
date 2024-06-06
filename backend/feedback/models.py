from django.db import models
from authentication_app.models import UserAccount

class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserAccount, on_delete=models.SET_NULL, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True)
    feedback_subject = models.CharField(max_length=255)
    message = models.TextField()
    submission_date = models.DateField(auto_now_add=True)
