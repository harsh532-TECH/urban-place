from django.db import models
from django.contrib.auth.models import User
from geopy.distance import geodesic

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    designation = models.CharField(max_length=50)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    reporting_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

class Broker(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # Link broker to an employee
    assigned_employee = models.ForeignKey('Employee', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

    def distance_to(self, latitude, longitude):
        broker_location = (self.latitude, self.longitude)
        user_location = (latitude, longitude)
        return geodesic(broker_location, user_location).meters

class Meeting(models.Model):
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    feedback = models.TextField()

    def __str__(self):
        return f"Meeting with {self.broker.name} on {self.date}"
