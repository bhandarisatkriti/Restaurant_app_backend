from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    Role_Choices=(
        ('customer','Customer'),
        ('staff','Staff'),
        ('owner','Owner')
    )
    role=models.CharField(max_length=10, choices=Role_Choices,default='customer')
    phone_number=models.CharField(max_length=20, blank='True')
    address=models.TextField(blank='True')

    def __str__(self):
        return f"{self.username} ({self.role})"
