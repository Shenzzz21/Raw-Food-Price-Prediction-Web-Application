from django.db import models
from authentication_app.models import UserAccount

class NewsletterMessage(models.Model):
    subject = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)
    sent_date = models.DateField(auto_now_add=True) 
    

class UserNewsletter(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(NewsletterMessage, on_delete=models.CASCADE)
