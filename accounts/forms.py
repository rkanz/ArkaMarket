from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class RegisterForm(UserCreationForm):
    first_name=forms.CharField(required=True,max_length=150,label="نام",
                               widget=forms.TextInput(attrs={"placeholder":"نام"}))
    last_name= forms.CharField(required=True, max_length=150,label="نام خانوادگی",
                               widget=forms.TextInput(attrs={"placeholder": "نام خانوادگی"}))
    email=forms.EmailField(required=True,label="ایمیل",
                           widget=forms.EmailInput(attrs={"placeholder": "example@email.com"}))
    username=forms.CharField(label="نام کاربری",
                             widget=forms.TextInput(attrs={"placeholder":"نام کاربری"})
                             )

    class Meta:
        model=User
        fields=("username","email","first_name","last_name",
                    "password1","password2")


    def clean_username(self):
        username=self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("این نام کاربری قبلا استفاده شده است")
        return username
    def clean_email(self):
        email=self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("این ایمیل قبلا ثبت شده است")
        return email
    def save(self,commit=True):
        user=super().save(commit=False)
        # map کردن data
        user.first_name=self.cleaned_data.get("first_name","").strip()
        user.last_name = self.cleaned_data.get("last_name", "").strip()
        user.email = self.cleaned_data.get("email", "").strip()
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    first_name=forms.CharField(
        required=True,
        max_length=150,
        label='نام',
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"نام"
        })
    )
    last_name=forms.CharField(
        required=True,
        max_length=150,
        label='نام خانوادگی ',
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"نام خانوادگی"
        })
    )
    phone=forms.CharField(
        required=False,
        max_length=20,
        label="شماره موبایل",
        widget=forms.TextInput(attrs={
            "class":"form-control",
            "placeholder":"شماره موبایل"
        })
    )
    address=forms.CharField(
        required=False,
        label='آدرس',
        widget=forms.Textarea(attrs={
            "class":"form-control",
            "placeholder":"آدرس",
            "rows":4
        })
    )
    class Meta:
        model=Profile
        fields=("phone","address")
    def __init__(self,*args,**kwargs):
        self.user=kwargs.pop("user",None)
        super().__init__(*args,**kwargs)

        if self.user:
            self.fields["first_name"].initial=self.user.first_name
            self.fields["last_name"].initial=self.user.last_name
            self.fields["phone"].initial=getattr(self.instance,"phone","")
            self.fields["address"].initial = getattr(self.instance, "address", "")
        elif self.user:
            pass
    def save(self,commit=True):

        if self.user:
            self.user.first_name=self.cleaned_data.get("first_name","").strip()
            self.user.last_name=self.cleaned_data.get("last_name","").strip()
            if commit:
                self.user.save()
        profile = super().save(commit=False)
        profile.phone=self.cleaned_data.get("phone","").strip()
        profile.address=self.cleaned_data.get("address","").strip()
        if commit:
            profile.save()
        return profile




