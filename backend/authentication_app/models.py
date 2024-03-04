# # models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import datetime

class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        # hashing password
        user.set_password(password)
        user.save()

        return user
    

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Add this line if missing

    # Additional fields
    registered_date = models.DateField(default=datetime.date.today)
    subscription_status = models.BooleanField(default=False)
    subscription_date = models.DateField(default=None, blank=True, null=True)  # Set to current date on object creation
   
    objects = UserAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def get_username(self):
        return self.name
    
    def __str__(self):
        return self.email
    
# class UserManager(BaseUserManager):
#     def _create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set.")
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_user(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_superuser", False)
#         return self._create_user(email, password, **extra_fields)

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault("is_superuser", True)
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")
#         return self._create_user(email, password, **extra_fields)

# class User(AbstractUser):
#     name = models.CharField(max_length=250)
#     email = models.CharField(max_length=250, unique=True)
#     password = models.CharField(max_length=250)

#     username = None
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []

#     objects = UserManager()

# class CustomUser(AbstractUser):
#     username = None
#     email = models.EmailField(('email address'), unique=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []