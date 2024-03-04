from django.db import models
from authentication_app.models import UserAccount

class OTP(models.Model):
    OTP_id = models.AutoField(primary_key=True)
    email = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    OTP_value = models.CharField(max_length=10)
    expiry_timestamp = models.DateTimeField()
