from django.contrib import admin
from .models import Profile, Group, Vehicle, Ride
# Register your models here.

admin.site.register(Profile)
admin.site.register(Group)
admin.site.register(Vehicle)
admin.site.register(Ride)