from django.db import models
from authentication_app.models import UserAccount

# class Newsletter(models.Model):
#     newsletter_id = models.AutoField(primary_key=True)
#     # email = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
#     email = models.EmailField(max_length=255, unique=True)
#     newsletter_subject = models.CharField(max_length=255)
#     newsletter_message = models.TextField()
#     sent_date = models.DateField(auto_now_add=True)

# class Subscribers(models.Model):
#     email = models.EmailField(null=True)
#     subscribed_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.email


class NewsletterMessage(models.Model):
    subject = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)
    sent_date = models.DateField(auto_now_add=True)  # Set to current date on object creation


    # def __str__(self):
    #     return self.subject


class UserNewsletter(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    newsletter = models.ForeignKey(NewsletterMessage, on_delete=models.CASCADE)
