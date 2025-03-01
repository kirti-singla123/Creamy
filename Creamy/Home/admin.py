import json
from django.contrib import admin
from .models import Product, Contact, Order

# Customize OrderAdmin to show order status, total amount, cart data, etc. in the list view
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'email_address',
        'order_status',
        'total_amount',
        'created_at',
        'cart_data_display'  # Add cart data display to the list view
    )
    list_filter = ('order_status', 'created_at')  # Filter orders by order_status and created_at
    search_fields = ('full_name', 'email_address', 'id')  # Enable search functionality in the admin panel
    ordering = ('-created_at',)  # Order by the latest created orders first

    # Specify the fields to be shown in the form (removed 'products' here)
    fields = (
        'full_name',
        'email_address',
        'phone_number',
        'address',
        'country',
        'state',
        'zip_code',
        'payment_method',
        'total_amount',
        'order_status',
        'cart_data',  # Include the cart data field
        'created_at'
    )

    readonly_fields = ('created_at',)  # Make the created_at field read-only

    def cart_data_display(self, obj):
        try:
            # Deserialize the cart_data string into a Python dictionary
            cart_data = json.loads(obj.cart_data) if obj.cart_data else {}

            # Extract only name, price, and quantity for each item
            simplified_cart_data = []
            for product in cart_data.values():
                # Only use the necessary fields: name, price, and quantity
                simplified_cart_data.append(
                    f"{product['name']} (Qty: {product['quantity']}, Price: ${product['price']})"
                )

            # Join the simplified cart data with a comma and return it
            # Truncate to 100 characters for better display in the admin panel
            return ', '.join(simplified_cart_data)[:100]  # Truncate to 100 characters

        except (TypeError, json.JSONDecodeError):
            return "Invalid Cart Data"


# Register your models with the admin site
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order, OrderAdmin)
