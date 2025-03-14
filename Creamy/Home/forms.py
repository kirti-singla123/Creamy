from django import forms
from django.core.validators import RegexValidator
from Home.models import Order  # Import the Order model

class OrderForm(forms.ModelForm):
    # Phone number field with validation using RegexValidator
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],  # This allows a phone number like +1 123 456 7890
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter phone number (e.g., +1 123 456 7890)',
            'type': 'tel',
        }),
    )

    # Zip code field with validation using RegexValidator
    zip_code = forms.CharField(
        max_length=10,
        validators=[RegexValidator(r'^[A-Za-z0-9\s\-]{3,10}$')],  # US-style zip code (e.g., 12345 or 12345-6789)
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter zip code',
            'type': 'text',
        }),
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email_address', 'phone_number', 'address', 'country', 'state', 'zip_code', 'payment_method', 'cc_name', 'cc_number', 'cc_expiration', 'cc_cvv', 'paypal_email', 'debit_name', 'debit_number', 'debit_expiration', 'debit_cvv', 'same_address', 'save_info', 'agreed_to_terms']

    # Custom clean method for phone_number
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        # Additional custom validation for phone number (e.g., minimum length, etc.)
        if len(phone_number) < 10:
            raise ValidationError('Phone number must be at least 10 digits long.')

        return phone_number

    # Custom clean method for zip_code
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')

        # Additional custom validation for zip code (e.g., length check, format, etc.)
        if len(zip_code) < 5:
            raise ValidationError('Zip code must be at least 5 characters long.')

        return zip_code
