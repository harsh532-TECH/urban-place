from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Meeting

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    password = forms.CharField(widget=forms.PasswordInput)

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['latitude', 'longitude']

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['employee', 'broker', 'date']
