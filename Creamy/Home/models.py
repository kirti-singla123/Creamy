from django.db import models
import json
from django.core.exceptions import ValidationError
from django.utils import timezone

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=150)
    price = models.FloatField()
    image = models.ImageField()

    def __str__(self):
        return self.name

    def to_dict(self):
        """Convert Product instance to a dictionary."""
        return {
            'product_id': self.id,
            'name': self.name,
            'price': self.price,
            'image': self.image.url if self.image else None,  # Ensure we get the image URL
        }


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


ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]


class Order(models.Model):
    # Customer Info
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Location
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, blank=True, null=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    # Extra Info
    same_address = models.BooleanField(default=False)
    save_info = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)

    # Order Data
    total_amount = models.FloatField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    products = models.ManyToManyField('Product', related_name='orders', blank=True)
    cart_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

    def save_cart_data(self, cart_items):
        """Convert Product instances to dict before saving to cart_data."""
        try:
            serialized_cart = [product.to_dict() for product in cart_items]
            self.cart_data = serialized_cart
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Invalid cart data: {str(e)}")

    def save(self, *args, **kwargs):
        # Basic validation
        if self.cart_data:
            if not isinstance(self.cart_data, list):
                raise ValidationError("Cart data must be a list.")
            for item in self.cart_data:
                if 'product_id' not in item or 'quantity' not in item:
                    raise ValidationError("Each cart item must include 'product_id' and 'quantity'.")

            # Update total amount
            self.total_amount = self.calculate_total_amount()

        super(Order, self).save(*args, **kwargs)

    def calculate_total_amount(self):
        total = 0
        cart_data = self.cart_data or []

        # Normalize product IDs
        product_ids = [
            item['product_id'].id if hasattr(item['product_id'], 'id') else item['product_id']
            for item in cart_data
        ]

        products = Product.objects.filter(id__in=product_ids)
        product_dict = {product.id: product for product in products}

        for item in cart_data:
            pid = item['product_id'].id if hasattr(item['product_id'], 'id') else item['product_id']
            quantity = item.get('quantity', 1)
            product = product_dict.get(pid)
            if product:
                total += product.price * quantity

        return total