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
    # Delivery Info
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email_address = models.EmailField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # Country Choices
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, blank=True, null=True)

    # State Choices
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)

    zip_code = models.CharField(max_length=20, blank=True, null=True)

    # Miscellaneous
    same_address = models.BooleanField(default=False)
    save_info = models.BooleanField(default=False)
    agreed_to_terms = models.BooleanField(default=False)

    total_amount = models.FloatField(default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    # Order status choices
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')

    # Many-to-Many relationship with Product model
    products = models.ManyToManyField('Product', related_name='orders', blank=True)

    # New cart_data field to store cart items as JSON
    cart_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

    def save_cart_data(self, cart_data):
        """Ensure that cart data is saved in JSON format."""
        try:
            # Ensure cart_data is a valid JSON serializable structure
            self.cart_data = json.dumps(cart_data)  # Convert to a JSON string
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Invalid cart data: {str(e)}")

    # Override the save method to ensure custom validation is run
    def save(self, *args, **kwargs):

        # Calculate the total amount before saving, avoiding recursion
        if not self.total_amount:  # Only calculate if not already set
            self.total_amount = self.calculate_total_amount()

        super(Order, self).save(*args, **kwargs)  # Proceed with saving the order

    # Method to dynamically calculate total amount based on cart
    def calculate_total_amount(self):
        total = 0
        cart_data = self.cart_data if self.cart_data else []

        # Fetch all products at once to avoid multiple database hits
        product_ids = [item['product_id'] for item in cart_data]  # Changed 'product_id' to 'id'
        products = Product.objects.filter(id__in=product_ids)

        product_dict = {product.id: product for product in products}

        # Calculate the total by matching product_id from the cart_data
        for item in cart_data:
            product = product_dict.get(item['product_id'])  # Changed 'product_id' to 'id'
            if product:
                total += product.price * item['quantity']

        return total
