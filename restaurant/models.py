from django.db import models

# Create your models here.
class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    logo = models.ImageField(upload_to='restaurant/', blank=True, null=True)
    phone = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_active=models.BooleanField(default=True)

    def __str__(self):
        return self.name