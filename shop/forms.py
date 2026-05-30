from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    honeypot=forms.CharField(required=False,widget=forms.HiddenInput)
    first_last_name=forms.CharField(
        label='نام و نام خانوادگی',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class':'form-control mt-1',
            'placeholder':'نام و نام خانوادگی',
        })
    )
    email=forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class':'form-control mt-1',
            'placeholder':'ایمیل شما'
        })
    )
    subject=forms.CharField(
        label='موضوع',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class':'form-control mt-1',
            'placeholder':'موضوع'
        })
    )
    message=forms.CharField(
        label='پیام',
        widget=forms.Textarea(attrs={
            'class':'form-control mt-1',
            'placeholder':'پیام',
            'rows': 8
        })
    )
    class Meta:
        model=ContactMessage
        fields=['first_last_name','email','subject','message']
    def clean_honeypot(self):
        value=self.cleaned_data.get('honeypot')
        if value:
            raise forms.ValidationError('Spam detected.Please leave this field blank.')
        return value

    def clean_name(self):
        name=self.cleaned_data.get('first_last_name')
        if not name or not name.strip():
            raise forms.ValidationError('وارد کردن نام و نام خانوادگی الزامی است.')
        return name

    def clean_email(self):
        email=self.cleaned_data.get('email')
        if not email or not email.strip():
            raise forms.ValidationError('وارد کردن ایمیل الزامی است.')
        return email

    def clean_message(self):
        message=self.cleaned_data.get('message')
        if not message or not message.strip():
            raise forms.ValidationError('وارد کردن پیام الزامی است.')
        return message
