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
        'payment_method',
        'total_amount',
        'order_status',
        'cart_data',  # Include the cart data field
        'created_at'
    )

    readonly_fields = ('created_at',)  # Make the created_at field read-only

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():  # Start a new transaction block
                # Add cart data from the session or other logic before saving
                if not obj.cart_data:
                    cart_data = get_cart(
                        request)  # Assume `get_cart()` is a utility function to retrieve cart data from the session
                    obj.cart_data = json.dumps(cart_data)

                # Debugging: Print cart data to the console
                print(f"Cart Data: {cart_data}")  # This will print the cart data to the console/log

                # Save the order
                obj.save()

                # Add products if it's a new order (not an update)
                if not change:
                    cart = json.loads(obj.cart_data)
                    for item in cart.values():
                        try:
                            product = Product.objects.get(id=item['product_id'])  # Assuming the cart has 'product_id'
                            obj.products.add(product)
                        except Product.DoesNotExist:
                            print(
                                f"Product with ID {item['product_id']} not found!")  # If the product ID doesn't exist, print a message

                super().save_model(request, obj, form, change)  # Continue the save operation after custom logic
        except Exception as e:
            print(f"Error during save: {e}")  # Log any errors that occur during the save process

    # Add cart_data_display method within the OrderAdmin class
    def cart_data_display(self, obj):
        try:
            # Deserialize the cart_data string into a Python dictionary
            cart_data = json.loads(obj.cart_data) if obj.cart_data else {}

            # Extract only name, price, and quantity for each item
            simplified_cart_data = []
            for product in cart_data.values():
                # Only use the necessary fields: name, price, and quantity

                name = product.get('name', 'Unknown Product')  # Default to 'Unknown Product' if name is missing
                price = product.get('price', 'N/A')
                quantity = product.get('quantity', 0)  # Default to 0 if quantity is missing

                # Append the simplified data
                simplified_cart_data.append(f"{name} (Qty: {quantity}, Price: ${price})")

            # Join the simplified cart data with a comma and return it
            # Truncate to 100 characters for better display in the admin panel
            return ', '.join(simplified_cart_data)[:100]  # Truncate to 100 characters

        except (TypeError, json.JSONDecodeError):
            return "Invalid Cart Data"


# Register your models with the admin site
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order, OrderAdmin)
