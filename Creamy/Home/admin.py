from django.contrib import admin
from .models import Product, Contact, Order

# Customize OrderAdmin to show order status, total amount, etc. in the list view
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email_address', 'order_status', 'total_amount', 'created_at')  # Show these fields in the list
    list_filter = ('order_status', 'created_at')  # Filter orders by order_status and created_at
    search_fields = ('full_name', 'email_address', 'id')  # Enable search functionality in the admin panel
    ordering = ('-created_at',)  # Order by the latest created orders first
    fields = ('full_name', 'email_address', 'phone_number', 'address', 'country', 'state', 'zip_code',
              'payment_method', 'total_amount', 'order_status', 'created_at')  # Specify the fields to be shown in the form
    readonly_fields = ('created_at',)  # Make the created_at field read-only


# Register your models with the admin site
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order, OrderAdmin)