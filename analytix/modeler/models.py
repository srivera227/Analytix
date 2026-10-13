from django.db import models

# Create your models here.
class ConexionBase(models.Model):
    host = models.CharField(max_length=500)
    port = models.IntegerField(max_length=10)
    dbname = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    password = models.CharField(max_length=30)
    status = models.BooleanField(default=True)
    motor = models.CharField(max_length=100, null=True, blank=True)
    lastConnection = models.DateTimeField(auto_created=True, null=True)
 


