from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Group, Vehicle, Ride
from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils import timezone
from .backend import VehicleInfo

class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

class ChangePasswordForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "password1", "password2"]

# Override clean() function in forms, to verify if the input is legal
# 生日clean一下
class ProfileForm(forms.ModelForm):
    dob = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'placeholder':"%d/%m/%Y",
                'type': "date",
                'class': "form-control"
            }
        )
    )
    class Meta:
        model = Profile
        fields = ['mobile', 'dob', 'gender']

class PersonalInfoForm(forms.ModelForm):
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

# PasswordForm()
class VehicleForm(forms.ModelForm):
    special_info = forms.CharField(
        label="Special information",
        required=False,
        widget=forms.Textarea(
            attrs={'cols': '10', 'rows': '1',
                   'placeholder': 'Optional special information about your car.'}),
        min_length=0,
        max_length=100,
    )
    class Meta:
        model = Vehicle
        fields = ["vehicleType", "plateNumber", "special_info"]

#检查一下passenger和vehicle是否匹配
class RideRequestForm(forms.ModelForm):
    dest = forms.CharField(
        label="Destination",
        widget=forms.Textarea(
            attrs={'cols': '10', 'rows': '1',
                   'placeholder': 'Enter your address here.'}),
        min_length=0,
        max_length=100,
    )

    special_req = forms.CharField(
        label="Special Requirement",
        required=False,
        widget=forms.Textarea(
            attrs={'cols': '10', 'rows': '1',
                   'placeholder': 'Optional special requirements.'}),
        min_length=0,
        max_length=100,
    )

    arrive_time = forms.DateTimeField(
        label="Desired Arrival Time",
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': "dd/mm/yyyy hh:mm",
                'type' : "datetime-local",
            }
        )
    )
    passengerNum = forms.IntegerField(
        label= "Passenger Number",
        widget=forms.NumberInput(
            attrs={'cols': '5', 'rows': '1',
                   'placeholder': 'Enter number here.'}),
        max_value=11, min_value=1
    )
    v_info = VehicleInfo()

    def clean_arrive_time(self):
        return self.cleaned_data.get('arrive_time').astimezone(timezone.utc)

    def clean_passengerNum(self):
        if self.cleaned_data.get('passengerNum') > 10:
            raise forms.ValidationError(
                "Max 10 people."
            )
        if self.cleaned_data.get('vehicleType'):
            if self.cleaned_data.get('passengerNum') + 1 > self.v_info.capacity[self.cleaned_data.get('vehicleType')]:
                raise forms.ValidationError(
                    "Too many passenger for this kind of car."
                )
        return self.cleaned_data.get('passengerNum')

    class Meta:
        model = Ride
        fields = ['dest', 'arrive_time', 'vehicleType',
                   'passengerNum', 'if_share', 'special_req']


class SearchRide(forms.Form):
    address = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Textarea(
            attrs={
                'name' : "address",
                'class' : "form-control",
                'type' : "text",
                'placeholder' : "Optional key words eg: NC Trinity Commons",
                'aria-label': "Username" ,
                'aria-describedby':"basic-addon1",
                'rows': '1',
            }
        )
    )

    start = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type': "datetime-local",
                'class': "form-control"
            }),
    )
    end = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type':"datetime-local",
                'class':"form-control"
            }),
    )
    passengerNum = forms.IntegerField(
        min_value=1, max_value=8,
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}),
    )

    def clean_start(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("start"):
            start = cleaned_data.get("start").astimezone(timezone.utc)
            if start < datetime.now().astimezone(timezone.utc):
                raise forms.ValidationError("start time or end time should be future times.")
        return  cleaned_data.get("start")

    def clean_end(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("start") and cleaned_data.get("end"):
            start = cleaned_data.get("start").astimezone(timezone.utc)
            end = cleaned_data.get("end").astimezone(timezone.utc)
            if end < start:
                raise forms.ValidationError("end time must be later than start time.")
        return cleaned_data.get("end")

class SearchTask(forms.Form):
    address = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.Textarea(
            attrs={
                'name' : "address",
                'class' : "form-control",
                'type' : "text",
                'placeholder' : "If left as empty, search all task between start and end",
                'aria-label': "Username" ,
                'aria-describedby':"basic-addon1",
                'rows': '1',
            }
        )
    )

    start = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type': "datetime-local",
                'class': "form-control"
            }),
    )
    end = forms.DateTimeField(
        input_formats=['%d/%m/%Y %H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type':"datetime-local",
                'class':"form-control"
            }),
    )

    def clean_start(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("start"):
            start = cleaned_data.get("start").astimezone(timezone.utc)
            if start < datetime.now().astimezone(timezone.utc):
                raise forms.ValidationError("start time or end time should be future times.")
        return  cleaned_data.get("start")

    def clean_end(self):
        cleaned_data = self.cleaned_data
        if cleaned_data.get("start") and cleaned_data.get("end"):
            start = cleaned_data.get("start").astimezone(timezone.utc)
            end = cleaned_data.get("end").astimezone(timezone.utc)
            if end < start:
                raise forms.ValidationError("end time must be later than start time.")
        return cleaned_data.get("end")