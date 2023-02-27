from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.forms import DateTimeInput

class CustomBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            if user.check_password(password):
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class VehicleInfo:
    capacity = [11, 4, 5, 2, 4, 7]
    type = [
            (0, 'Not required'),
            (1, 'Sedan'),  #4
            (2, 'SUV'),  #4
            (3, 'Coupe'),  #2
            (4, 'Hatchback'),  #4
            (5, 'Mini van'),  #7
            ]
    description = "-Sedan: 4 door trunks, capacity: 4 <br/>\
        -SUV: Sport-Utility Vehicle, capacity: 5 <br/>\
        -Coupe: 2 door trunks, capacity: 2 <br/>\
        -Hatchback: Compact sedan, capacity: 4 <br/>\
        -Minivan: Trunks with large cargo area, capacity: 7 <br/>\
        * The capacity includes driver. "
