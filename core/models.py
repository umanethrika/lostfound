from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import RegexValidator
import re

phone_validator = RegexValidator(r'^\+?\d{10,15}$', "Enter a valid phone number")



LOCATIONS = [
    ("hostel", "Hostel"),
    ("library", "Central Library"),
    ("sports", "Sports Complex"),
    ("academic", "Academic Building"),
    ("others", "Others"),
]

CATEGORY_CHOICES = [
    ("electronics", "Electronics"),
    ("stationery", "Stationery"),
    ("wallets", "Wallets & Accessories"),
    ("books", "Books"),
    ("id_cards", "ID Cards"),
    ("keys", "Keys"),
    ("clothing", "Clothing"),
    ("others", "Others"),
]

# ✅ Validator for @kgpian.iitkgp.ac.in emails
def validate_kgpian_email(value):
    if not re.match(r"^[\w\.-]+@kgpian\.iitkgp\.ac\.in$", value):
        raise ValidationError("Email must end with @kgpian.iitkgp.ac.in")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, roll_number, name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        validate_kgpian_email(email)   # enforce @kgpian.iitkgp.ac.in domain

        user = self.model(email=email, roll_number=roll_number, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, roll_number, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, roll_number, name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, validators=[validate_kgpian_email])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # ✅ Login with email
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["roll_number", "name"]

    def __str__(self):
        return f"{self.name} ({self.roll_number})"

# ----------------------------
# Lost & Found Models
# ----------------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    LOST = "LOST"
    FOUND = "FOUND"
    KIND_CHOICES = [
        (LOST, "Lost"),
        (FOUND, "Found"),
    ]

    user = models.ForeignKey("core.CustomUser", on_delete=models.CASCADE)  # linked to custom user
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=5, choices=KIND_CHOICES)
    # category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Others")
    location = models.CharField(max_length=50, choices=LOCATIONS)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    contact_info = models.CharField(max_length=200, validators=[phone_validator])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kind} - {self.title}"


class MatchNotification(models.Model):
    lost_item = models.ForeignKey(
        Item, related_name="lost_matches", on_delete=models.CASCADE
    )
    found_item = models.ForeignKey(
        Item, related_name="found_matches", on_delete=models.CASCADE
    )
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.lost_item.title} ↔ {self.found_item.title}"


