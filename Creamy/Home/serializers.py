from rest_framework import serializers
from Home.models import Order, Product


# ProductOrderSerializer: This serializer handles each product's details in the order (within cart_data)
class ProductOrderSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())  # Product reference
    quantity = serializers.IntegerField()
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
    cart_data = ProductOrderSerializer(many=True, required=True)

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
        """Override the create method to handle total calculation and save cart data."""
        # Extract cart data
        cart_data = validated_data.pop('cart_data')  # Remove cart data from validated data

        # Create the Order instance (without cart_data for now)
        order = Order.objects.create(**validated_data)

        total_amount = 0  # Initialize total amount

        # Prepare cart data with serializable product details
        serialized_cart_data = []

        # Calculate the total amount from cart_data
        for item in cart_data:
            product = item['product_id']  # Get the product object
            quantity = item['quantity']
            total = product.price * quantity  # Calculate total for this product

            # Add the product to the order (many-to-many relationship)
            order.products.add(product)  # Add product to the many-to-many relationship

            # Accumulate total for the entire order
            total_amount += total

            # Serialize product data to save it in cart_data (ensure only necessary fields are included)
            serialized_item = {
                'product_id': product.id,  # Store only the product ID
                'name': product.name,  # Store the product name
                'price': product.price,  # Store the product price
                'quantity': quantity,  # Store the quantity
                'total_price': total  # Store the total price for this product
            }
            serialized_cart_data.append(serialized_item)

        # Save the total amount to the order
        order.total_amount = total_amount
        order.save()

        # Save the cart data to the order (as a JSON serializable structure)
        order.save_cart_data(serialized_cart_data)
        order.save()  # Save the order with cart data

        return order

    def update(self, instance, validated_data):
        """Override to handle update logic (if needed)."""
        cart_data = validated_data.pop('cart_data', None)  # If cart_data exists, pop it

        # Update the instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # If cart_data exists, process it
        if cart_data is not None:
            total_amount = 0  # Initialize total amount for the updated cart data

            # Clear existing products to recalculate (if needed)
            instance.products.clear()

            # Calculate the new total amount from cart_data
            for item in cart_data:
                product_id = item['product_id']
                quantity = item['quantity']

                # Fetch the product instance by ID
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise ValidationError(f"Product with ID {product_id} does not exist.")

                total = product.price * quantity  # Calculate total for this product
                total_amount += total

                # Add the product to the order (many-to-many relationship)
                instance.products.add(product)

            # Update the total amount and save the cart data
            instance.total_amount = total_amount
            instance.save_cart_data(cart_data)

        # Save the updated order instance
        instance.save()

        return instance

