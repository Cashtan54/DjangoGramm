from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import User, Post, Image


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username')


class MyUserChangeForm(forms.Form):
    bio = forms.CharField(max_length=250, required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('profile_photo', 'bio')


class CreatePostForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'rows': 5,
                                                        'cols': 50,
                                                        'placeholder': 'Put your text here'}),
                           required=False)
    images = forms.ImageField()



