from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, Item, Category, LOCATIONS
import re


# ✅ Password strength checker
def strong_password(value):
    if len(value) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", value):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", value):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not re.search(r"[0-9]", value):
        raise ValidationError("Password must contain at least one number")
    if not re.search(r"[@$!%*?&]", value):
        raise ValidationError("Password must contain at least one special character (@$!%*?&)")


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password", 
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}), 
        validators=[strong_password]
    )
    password2 = forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput(attrs={"placeholder": "Re-enter password"})
    )

    class Meta:
        model = CustomUser
        fields = ("name", "roll_number", "email")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "roll_number": forms.TextInput(attrs={"placeholder": "Roll Number"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email (must end with @kgpian.iitkgp.ac.in)"}),
        }

    # ✅ Email domain validation
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith("@kgpian.iitkgp.ac.in"):
            raise ValidationError("Email must end with @kgpian.iitkgp.ac.in")
        return email

    # ✅ Password confirmation validation
    def clean_password2(self):
        p1 = self.cleaned_data.get("password1")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match")
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", 
        widget=forms.EmailInput(attrs={"placeholder": "Email (must end with @kgpian.iitkgp.ac.in)"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )

    # ✅ Restrict login to KGPian email
    def clean_username(self):
        email = self.cleaned_data.get("username")
        if not email.endswith("@kgpian.iitkgp.ac.in"):
            raise ValidationError("Only @kgpian.iitkgp.ac.in emails are allowed")
        return email

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ["title", "description", "kind", "category", "location", "image", "contact_info"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Item title"}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "Description (brand, color, etc.)", "rows": 3}),
            "kind": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "location": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "contact_info": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
        }