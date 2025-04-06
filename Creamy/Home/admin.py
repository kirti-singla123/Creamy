import json
from django.contrib import admin
from .models import Product, Contact, Order
from django.db import transaction  # Ensure transaction is imported if you're using it

class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'email_address',
        'order_status',
        'total_amount',
        'created_at',
        'cart_data_display',  # Add cart data display to the list view
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
        'total_amount',
        'order_status',
        'cart_data',  # Include the cart data field
        'created_at'
    )

    readonly_fields = ('created_at',)  # Make the created_at field read-only

    # Custom method to display cart data in the admin panel
    def cart_data_display(self, obj):
        try:
            # Deserialize the cart_data string into a Python list (not a dictionary)
            cart_data = json.loads(obj.cart_data) if obj.cart_data else []

            # Ensure cart_data is a list and contains expected data
            if isinstance(cart_data, list):
                simplified_cart_data = []
                for product in cart_data:
                    # Only use the necessary fields: name, price, and quantity
                    name = product.get('name', 'Unknown Product')  # Default to 'Unknown Product' if name is missing
                    price = product.get('price', 'N/A')
                    quantity = product.get('quantity', 0)  # Default to 0 if quantity is missing

                    # Append the simplified data
                    simplified_cart_data.append(f"{name} (Qty: {quantity}, Price: ${price})")

                # Join the simplified cart data with a comma and return it
                # Truncate to 100 characters for better display in the admin panel
                return ', '.join(simplified_cart_data)[:100]  # Truncate to 100 characters
            else:
                return "Invalid Cart Data: Expected a list."
        except (TypeError, json.JSONDecodeError):
            return "Invalid Cart Data"  # Return a fallback message if there is an error

    # Save method to handle cart data serialization before saving the order
    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():  # Start a new transaction block
                if not obj.cart_data:
                    cart_data = get_cart(request)  # Assuming get_cart() is a utility function to retrieve cart data
                    obj.cart_data = json.dumps(cart_data)

                obj.save()

                # Add products if it's a new order (not an update)
                if not change:
                    cart = json.loads(obj.cart_data)
                    for item in cart:
                        try:
                            product = Product.objects.get(id=item['product_id'])
                            obj.products.add(product)
                        except Product.DoesNotExist:
                            print(f"Product with ID {item['product_id']} not found!")

                super().save_model(request, obj, form, change)  # Continue the save operation after custom logic
        except Exception as e:
            print(f"Error during save: {e}")  # Log any errors that occur during the save process

# Register your models with the admin site
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order, OrderAdmin)
