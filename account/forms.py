from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , UserChangeForm
from django.contrib.auth.models import User
from django.forms import ValidationError
from django import forms

from django.forms.widgets import TextInput, PasswordInput

class CreateUserForm(UserCreationForm):
    class Meta:
        model= User
        fields= ['username', 'email' , 'password1' , 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required= True

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email= email).exclude(pk=self.user.pk).exists():
            raise ValidationError('this email is already used')
        
        if len(email) >= 350:
            raise ValidationError('the email is too long')
        
        return email

class LoginForm(AuthenticationForm):
    username= forms.CharField(widget=TextInput())
    password= forms.CharField(widget=PasswordInput())

class UpdateForm(forms.ModelForm):

    password= None

    def __init__(self, *args, **kwargs):
            super(UpdateForm, self).__init__(*args, **kwargs)
            self.fields['email'].required= True
        
    class Meta:
        model= User
        fields= ['username', 'email']
        exclude= ['password1','password2']

    