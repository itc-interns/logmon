from django.db import models

# Create your models here.

class  daily_bandwidth(models.Model):
    day = models.CharField(max_length=5)
    bandwidth = models.CharField(max_length=30)