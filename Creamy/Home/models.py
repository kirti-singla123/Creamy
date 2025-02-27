from django.db import models
from django.utils import timezone
import json
# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField()

    def __str__(self):
        return self.name


class Contact(models.Model):
    name = models.CharField(max_length=120)
    email = models.CharField(max_length=120)
    phone = models.CharField(max_length=12)
    message = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name

# Define choices outside the model for readability
COUNTRY_CHOICES = [
    ('US', 'United States'),
    ('CA', 'Canada'),
    ('GB', 'United Kingdom'),
    ('IN', 'India'),
    ('AU', 'Australia'),
]

STATE_CHOICES = [
    ('CA', 'California'),
    ('NY', 'New York'),
    ('TX', 'Texas'),
    ('FL', 'Florida'),
    ('IL', 'Illinois'),
]

PAYMENT_CHOICES = [
    ('credit', 'Credit Card'),
    ('debit', 'Debit Card'),
    ('paypal', 'PayPal'),
]

ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    # Delivery Info
    full_name = models.CharField(max_length=100, default=" ")
    email_address = models.EmailField(max_length=255, default=" ")
    phone_number = models.CharField(max_length=15, default=" ")
    address = models.CharField(max_length=255, default=" ")

    # Country Choices
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default=" ")

    # State Choices
    state = models.CharField(max_length=2, choices=STATE_CHOICES, default=" ")

    zip_code = models.CharField(max_length=20, default="")

    # Payment Info
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='credit')

    # Credit Card Fields
    cc_name = models.CharField(max_length=100, blank=True, null=True)
    cc_number = models.CharField(max_length=20, blank=True, null=True)
    cc_expiration = models.CharField(max_length=5, blank=True, null=True)  # MM/YY
    cc_cvv = models.CharField(max_length=4, blank=True, null=True)

    # PayPal Fields
    paypal_email = models.EmailField(blank=True, null=True)

    # Debit Card Fields
    debit_name = models.CharField(max_length=100, blank=True, null=True)
    debit_number = models.CharField(max_length=20, blank=True, null=True)
    debit_expiration = models.CharField(max_length=5, blank=True, null=True)  # MM/YY
    debit_cvv = models.CharField(max_length=4, blank=True, null=True)

    # Miscellaneous
    same_address = models.BooleanField(default=False)
    save_info = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    # Order status choices
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

