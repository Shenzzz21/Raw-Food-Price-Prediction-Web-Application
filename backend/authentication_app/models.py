from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import datetime

# User Model Manager
class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        # Ensure that an email address is provided
        if not email:
            raise ValueError('Users must have an email address')

        # Normalize email address (convert to lowercase)
        email = self.normalize_email(email)
        # Create a new user instance with email and name
        user = self.model(email=email, name=name)

        # Hash the password and save the user
        user.set_password(password)
        user.save()

        return user
    

    def create_superuser(self, email, name, password=None):
        # Create a superuser with provided email, name, and password
        user = self.create_user(email, name, password)
        # Assign staff and superuser permissions
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

# Custom User Model
class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    registered_date = models.DateField(default=datetime.date.today)
    subscription_status = models.BooleanField(default=False)
    subscription_date = models.DateField(default=None, blank=True, null=True)
   
    # Set the custom manager for user objects
    objects = UserAccountManager()

    # Specify the field used as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_username(self):
        return self.name
    
    def __str__(self):
        return self.email