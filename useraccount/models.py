import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager 
from django.db import models


# CHANGE: Rename class to CustomUserManager and inherit from BaseUserManager
class CustomUserManager(BaseUserManager): 
    def _create_user(self, name, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not specified a valid email address")
        
        email = self.normalize_email(email)
        user = self.model(name=name,email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(name, email, password, **extra_fields)
    
    def create_superuser(self, name=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(name, email, password, **extra_fields)
    
    
class User(AbstractUser, PermissionsMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='upload/avatars/', blank=True, null=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='useraccount_set', # Unique related_name for Group access
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='useraccount_permissions_set', # Unique related_name for Permission access
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager() 

   