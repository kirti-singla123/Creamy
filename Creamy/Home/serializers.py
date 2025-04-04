from rest_framework import serializers
from Home.models import Order, Product

# ProductOrderSerializer: This serializer handles each product's details in the order (within cart_data)
class ProductOrderSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Product reference
    quantity = serializers.IntegerField()
    total = serializers.FloatField(required=False)  # This will be calculated based on quantity and product price
    name = serializers.CharField(max_length=255, required=False)  # Optional, from Product
    price = serializers.FloatField(required=False)  # Optional, from Product
    image = serializers.CharField(max_length=255, required=False)  # Optional, from Product

    def validate_total(self, value):
        """Ensure the total is greater than 0"""
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than 0.")
        return value

    def calculate_total(self, product, quantity):
        """Calculate the total for the product based on its price and quantity"""
        return product.price * quantity

# OrderSerializer: Handles the entire order creation logic, including cart data and total calculation
class OrderSerializer(serializers.ModelSerializer):
    cart_data = ProductOrderSerializer(many=True)  # Expecting a list of cart items (products)

    class Meta:
        model = Order
        fields = [
            'id',
            'full_name',
            'email_address',
            'phone_number',
            'address',
            'country',
            'state',
            'zip_code',
            'same_address',
            'save_info',
            'agreed_to_terms',
            'total_amount',
            'created_at',
            'order_status',
            'cart_data'  # List of cart items
        ]

    def create(self, validated_data):
        """Override the create method to handle total calculation and save cart data"""
        # Extract cart data
        cart_data = validated_data.pop('cart_data')  # Remove cart data from validated data

        # Create the Order instance (without cart_data for now)
        order = Order.objects.create(**validated_data)

        total_amount = 0  # Initialize total amount

        # Calculate the total amount from cart_data
        for item in cart_data:
            product = item['product_id']  # Get the product object
            quantity = item['quantity']
            total = product.price * quantity  # Calculate total for this product

            # Add the product to the order (many-to-many relationship)
            order.products.add(product)  # Add product to the many-to-many relationship

            # Accumulate total for the entire order
            total_amount += total

        # Save the total amount to the order
        order.total_amount = total_amount
        order.save()

        # Save the cart data to the order
        order.save_cart_data(cart_data)
        order.save()  # Save the order with cart data

        return order

    def update(self, instance, validated_data):
        """Override to handle update logic (if needed)"""
        cart_data = validated_data.pop('cart_data', None)  # If cart_data exists, pop it

        # Update the instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If cart_data exists, process it
        if cart_data is not None:
            total_amount = 0  # Initialize total amount for the updated cart data

            # Calculate the new total amount from cart_data
            for item in cart_data:
                product = item['product_id']
                quantity = item['quantity']
                total = product.price * quantity  # Calculate total for this product
                total_amount += total

            # Update the total amount and save the cart data
            instance.total_amount = total_amount
            instance.save_cart_data(cart_data)

        # Save the updated order instance
        instance.save()

        return instance
