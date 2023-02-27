from django.conf import settings
from django.db import models
from django.utils import timezone
from .backend import VehicleInfo
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class Profile(models.Model):
    user = models.OneToOneField(User, null=True, related_name='profile', on_delete=models.CASCADE)
    mobile = PhoneNumberField()
    dob = models.DateField()
    gender_choices = [
        (0, 'female'),
        (1, 'male'),
        (2, 'prefer not to tell')
    ]
    gender = models.IntegerField(choices=gender_choices)

    def __str__(self):
        return self.user.username

    def get_gender(self):
        if self.gender is None:
            return "Unknown"
        else:
            return self.gender_choices[self.gender][1]

class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groupNum = models.IntegerField(blank=False, null=False)
    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name +' '+ '(' + str(self.groupNum) + ')'

class Vehicle(models.Model):
    vehicle_info = VehicleInfo()
    vehicleType = models.IntegerField(choices=vehicle_info.type, help_text=vehicle_info.description)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vehicle', default=None)
    plateNumber = models.CharField(max_length=20)
    special_info = models.TextField(max_length=100, blank=True, default='')

    def get_type(self):
        return self.vehicle_info.type[self.vehicleType][1]

    def get_capacity(self):
        return self.vehicle_info.capacity[self.vehicleType]

class Ride(models.Model):
    # search first if not find create a new one
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    passengerNum = models.IntegerField(default=1)
    # .add()
    # check if already in the ride
    shared_by_user = models.ManyToManyField(Group, blank=True, default=None)
    vehicle_info = VehicleInfo()

    vehicleType = models.IntegerField(choices=vehicle_info.type, help_text=vehicle_info.description)
    dest = models.TextField(max_length=100)
    special_req = models.TextField(max_length=100, blank=True, default='')
    arrive_time = models.DateTimeField()
    if_share = models.BooleanField()
    
    # status
    completed = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    # vehicle
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, default=None, blank=True, null=True)
    # vehicle
    
    def __str__(self):
        return str(self.pk)

    def get_passenger_num(self):
        total = 0
        for group in self.shared_by_user.all():
            total+=group.groupNum
        return total

    def get_v_type(self):
        return self.vehicle_info.type[self.vehicleType][1]

    def get_capacity(self):
       return self.vehicle_info.capacity[self.vehicleType]



        