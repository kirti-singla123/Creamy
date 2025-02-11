# forms.py
from django import forms
from Home.models import Order  # Import the Order model


from django import forms
from Home.models import Order  # Import the Order model

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email_address', 'phone_number', 'address',
                  'country', 'state', 'zip_code', 'payment_method', 'cc_name', 'cc_number',
                  'cc_expiration', 'cc_cvv', 'paypal_email', 'debit_name', 'debit_number',
                  'debit_expiration', 'debit_cvv']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the initial state choices based on selected country
        country = self.initial.get('country', 'US')  # Default to 'US' if not set
        self.fields['state'].choices = self.get_state_choices(country)

        # Make payment-related fields conditionally required based on the selected payment method
        self.fields['cc_name'].required = False
        self.fields['cc_number'].required = False
        self.fields['cc_expiration'].required = False
        self.fields['cc_cvv'].required = False
        self.fields['paypal_email'].required = False
        self.fields['debit_name'].required = False
        self.fields['debit_number'].required = False
        self.fields['debit_expiration'].required = False
        self.fields['debit_cvv'].required = False

    def get_state_choices(self, country_code):
        # You can define state choices based on the country code
        if country_code == 'US':
            return [
                ('CA', 'California'),
                ('NY', 'New York'),
                ('TX', 'Texas'),
                ('FL', 'Florida'),
                ('IL', 'Illinois'),
            ]
        elif country_code == '':
            return [
                ('ON', 'Ontario'),
                ('QC', 'Quebec'),
                ('BC', 'British Columbia'),
                ('AB', 'Alberta'),
            ]
        # Add more countries and states as needed
        return []

    def clean(self):
        # Get the cleaned data before performing any modifications
        cleaned_data = super().clean()

        payment_method = cleaned_data.get('payment_method')

        # Remove unnecessary payment fields based on the selected payment method
        if payment_method == 'credit':
            # Keep only credit card fields and clear others
            cleaned_data['paypal_email'] = None
            cleaned_data['debit_name'] = None
            cleaned_data['debit_number'] = None
            cleaned_data['debit_expiration'] = None
            cleaned_data['debit_cvv'] = None
        elif payment_method == 'paypal':
            # Keep only PayPal email and clear others
            cleaned_data['cc_name'] = None
            cleaned_data['cc_number'] = None
            cleaned_data['cc_expiration'] = None
            cleaned_data['cc_cvv'] = None
            cleaned_data['debit_name'] = None
            cleaned_data['debit_number'] = None
            cleaned_data['debit_expiration'] = None
            cleaned_data['debit_cvv'] = None
        elif payment_method == 'debit':
            # Keep only debit card fields and clear others
            cleaned_data['cc_name'] = None
            cleaned_data['cc_number'] = None
            cleaned_data['cc_expiration'] = None
            cleaned_data['cc_cvv'] = None
            cleaned_data['paypal_email'] = None
        else:
            # If no payment method selected, clear all payment-related fields
            cleaned_data['cc_name'] = None
            cleaned_data['cc_number'] = None
            cleaned_data['cc_expiration'] = None
            cleaned_data['cc_cvv'] = None
            cleaned_data['paypal_email'] = None
            cleaned_data['debit_name'] = None
            cleaned_data['debit_number'] = None
            cleaned_data['debit_expiration'] = None
            cleaned_data['debit_cvv'] = None

        return cleaned_data
