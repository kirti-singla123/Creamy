from django import forms
from Home.models import Order  # Import the Order model

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email_address', 'phone_number', 'address', 'country', 'state', 'zip_code', 'payment_method', 'cc_name', 'cc_number', 'cc_expiration', 'cc_cvv', 'paypal_email', 'debit_name', 'debit_number', 'debit_expiration', 'debit_cvv', 'same_address', 'save_info', 'agreed_to_terms']