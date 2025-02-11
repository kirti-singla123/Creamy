from django.db import models
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



class Order(models.Model):
    # Delivery Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_address = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    # Country Choices (You can add more countries to this list)
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('GB', 'United Kingdom'),
        ('IN', 'India'),
        ('AU', 'Australia'),
        # Add more countries as needed
    ]
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)

    # State Choices (You can add more states or dynamic states based on country)
    STATE_CHOICES = [
        ('CA', 'California'),
        ('NY', 'New York'),
        ('TX', 'Texas'),
        ('FL', 'Florida'),
        ('IL', 'Illinois'),
        # Add more states or dynamically generate based on country
    ]
    state = models.CharField(max_length=2, choices=STATE_CHOICES)

    zip_code = models.CharField(max_length=20)

    # Payment Info
    PAYMENT_CHOICES = [
        ('credit', 'Credit Card'),
        ('debit', 'Debit Card'),
        ('paypal', 'PayPal'),
    ]
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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.first_name} {self.last_name}"
