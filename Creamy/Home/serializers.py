from rest_framework import serializers
from Home.models import Order, Product
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from decimal import Decimal  # Add this import


class ProductOrderSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

    # Optional fields for display
    name = serializers.CharField(max_length=255, required=False)
    price = serializers.FloatField(required=False)
    image = serializers.CharField(max_length=255, required=False)

    def validate(self, data):
        """Custom validation logic"""
        product = data.get('product_id')
        quantity = data.get('quantity')

        if not product:
            raise ValidationError("Product ID is required.")
        if quantity is None or quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

        return data

    @staticmethod
    def calculate_total(product, quantity):
        """Calculate the total for the product based on its price and quantity"""
        return product.price * quantity

    def to_representation(self, instance):
        """
        Custom representation to avoid .pk errors.
        """
        product = instance.get('product_id')
        quantity = instance.get('quantity')

        if isinstance(product, Product):
            return {
                'product_id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image.url if hasattr(product, 'image') and product.image else ''
            }
        else:
            # Fallback if not passed a full product
            return {
                'product_id': product,
                'name': instance.get('name'),
                'price': float(instance.get('price', 0)),
                'quantity': quantity,
                'image': instance.get('image', '')
            }

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
            'cart_data',
        ]

    def create(self, validated_data):
        """Override the create method to handle total calculation and save cart data."""
        print("Validated data:", validated_data)

        cart_data = validated_data.pop('cart_data', None)

        if not cart_data:
            raise ValidationError("Cart data is missing or malformed.")

        # Create the Order instance
        order = Order.objects.create(**validated_data)

        total_amount = Decimal('0.00')
        serialized_cart_data = []

        for item in cart_data:
            product = item.get('product_id')  # Already a Product instance, thanks to PrimaryKeyRelatedField

            if not isinstance(product, Product):
                raise ValidationError(f"Invalid product {product}. Expected a Product instance.")

            # No need to do get_object_or_404 again — DRF already fetched it
            item['product'] = product  # Optional: if you need it elsewhere

            quantity = item.get('quantity')
            if quantity is None or quantity <= 0:
                raise ValidationError(f"Invalid quantity {quantity}. It must be a positive integer.")

            total = Decimal(product.price) * Decimal(quantity)

            order.products.add(product)

            serialized_item = {
                'product_id': product.id,
                'name': product.name,
                'price': float(product.price),  # 👈 Convert to float
                'quantity': quantity,
                'total_price': float(total),  # 👈 Convert to float
            }

            serialized_cart_data.append(serialized_item)
            total_amount += total

        # Save cart data and total to the order
        order.cart_data = serialized_cart_data
        order.total_amount = float(total_amount)  # 👈 Convert to float if total_amount is used in JSONField
        order.save()

        return order