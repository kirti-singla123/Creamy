from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Contact
from Home.models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.conf import settings
import json
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import re
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Home.serializers import OrderSerializer
from Home.models import COUNTRY_CHOICES, STATE_CHOICES  # Import the choices from models.py
from django.views.decorators.csrf import csrf_exempt


# Set your Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


# View for Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to home or another page after login
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


# Function to check password strength
def is_strong_password(password):
    # Add your password strength checking logic here
    return (len(password) >= 8 and any(char.isdigit() for char in password)
            and any(char in '!@#$%^&*()_+' for char in password))


# Function to check if password is too similar to username or email
def is_password_similar(username, password, confirm_password):
    return username.lower() in password.lower() or password.lower() == confirm_password.lower()


# View for Sign Up
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Extract cleaned data (username, password, confirm password)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            confirm_password = form.cleaned_data['password2']  # This is the confirm password field

            # Check if password is strong enough
            if not is_strong_password(password):
                form.add_error(
                    'password1',
                    "Password is too weak. It should have at least 8 characters, a number, and a special character.")

            # Check if password and confirm password match
            elif password != confirm_password:
                form.add_error('password2', "The passwords do not match.")

            # If no errors, save the user and log them in
            if not form.errors:
                # Save the user object
                user = form.save()

                # Log the user in automatically
                login(request, user)

                # Redirect to the homepage or any page you prefer
                return redirect('home')  # Change 'home' to whatever URL you want the user to be redirected to
        else:
            print("Form errors:", form.errors)  # Debugging errors

        # Return the form with errors back to the sign-up page
        return render(request, 'signup.html', {'form': form, 'error': form.errors})
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the homepage after logout


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def product_list(request):
    products = Product.objects.all()
    return render(request, 'product.html', {'products': products})


# Helper function to get the cart
def get_cart(request):
    return request.session.get('cart', {})


# Add to Cart view
def add_to_cart(request, product_id):
    cart = get_cart(request)  # Fetch or initialize the cart from the session

    # Get the product by ID or return a 404 if it does not exist
    product = get_object_or_404(Product, id=product_id)

    price = float(product.price)

    # Check if the product is already in the cart, if so, increment the quantity
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1  # Increment the quantity
    else:
        # Add the product to the cart session with all required fields
        cart[str(product.id)] = {
            'name': product.name,
            'price': float(product.price),  # Ensure price is stored as a float
            'quantity': 1,  # Default to 1 when adding a product
            'image': product.image.url if product.image else None,  # Use the URL if the image exists
            'product_id': product.id,  # Ensure this field is added to the cart
        }

    # Save the updated cart back into session
    request.session['cart'] = cart

    # Debugging: Output the updated cart structure to the console
    print("Updated Cart:", cart)

    # Redirect to the cart page
    return redirect('cart')


# Cart view
def cart(request):
    cart = get_cart(request)  # Get the cart from the session
    # Calculate the total price only once
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())
    products_in_cart = []  # List to store products in cart along with details

    # Debugging: Output the structure of the cart
    print("Cart structure:", cart)

    # Loop through each item in the cart
    for product_id, item in cart.items():
        # Debugging: Output each product_id and item
        print(f"Processing product ID: {product_id} with item: {item}")

        # Check if 'product_id' exists in the item
        if 'product_id' in item:
            # Fetch the product details from the Product model
            try:
                product = Product.objects.get(id=item['product_id'])  # Get product by ID
                # Add the full product object to the item
                item['product'] = product
                item['total'] = product.price * item['quantity']  # Calculate total price for this item
                products_in_cart.append(item)  # Append this item to the products_in_cart list
            except Product.DoesNotExist:
                print(f"Error: Product with ID {item['product_id']} not found.")
        else:
            # If 'product_id' is missing, print a warning
            print(f"Warning: 'product_id' not found in item: {item}")

    # Prepare the cart data in JSON format for JavaScript
    cart_data = {
        product_id: {
            'product_id': product_id,
            'name': item['product'].name if 'product' in item else '',
            'price': item['product'].price if 'product' in item else 0,
            'quantity': item['quantity'],
            'total': item.get('total', 0),
            'image': item['product'].image.url if 'product' in item and item['product'].image else ''
        }
        for product_id, item in cart.items()
    }

    # Ensure that the cart_data is serializable
    cart_data_serializable = {
        product_id: {
            'product_id': product_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item['total'],
            'image': item['image']
        }
        for product_id, item in cart_data.items()
    }

    # Serialize the cart data into JSON
    cart_json = json.dumps(cart_data_serializable)
    # Debugging: Log the serialized cart JSON
    print("Serialized cart JSON:", cart_json)

    # Render the cart page with the cart data and total price
    return render(request, 'cart.html', {
        'cart': cart,
        'total_price': total_price,
        'cart_json': cart_json  # Pass serialized cart data to template
    })


# Remove from Cart view
def remove_from_cart(request, product_id):
    cart = get_cart(request)

    # If the product exists in the cart, remove it
    if str(product_id) in cart:
        del cart[str(product_id)]

    # Save the updated cart back into the session
    request.session['cart'] = cart

    # Redirect to the cart page
    return redirect('cart')


# Decrease quantity view
def decrease_quantity(request, product_id):
    cart = get_cart(request)

    # If the product exists in the cart and quantity is greater than 1, decrease the quantity
    if str(product_id) in cart and cart[str(product_id)]['quantity'] > 1:
        cart[str(product_id)]['quantity'] -= 1
        # Save the updated cart back into the session
        request.session['cart'] = cart

    # Redirect to the cart page
    return redirect('cart')


def increase_quantity(request, product_id):
    # Retrieve cart from session
    cart = request.session.get('cart', {})

    # Convert the product_id to a string to match the keys in the session cart
    product_id_str = str(product_id)

    # Debugging: Print the cart before update
    print(f"Cart before: {cart}")

    # Ensure the product exists in the cart
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1  # Increase quantity

    # Save the updated cart to session
    request.session['cart'] = cart
    request.session.modified = True  # Explicitly mark session as modified

    # Redirect back to the cart
    return redirect('cart')


def checkout(request):
    if request.method == 'POST':
        # Retrieve the cart from the session
        cart = get_cart(request)

        # Debug print for cart contents
        print("Cart contents:", cart)

        if not isinstance(cart, dict):
            cart = {}  # Reset to an empty dictionary if cart is not a dict

        if not cart:
            cart_json = "[]"  # Empty JSON array if no cart items exist
        else:
            # Convert cart dictionary to JSON string
            cart_json = json.dumps(cart)  # Properly convert the cart into a JSON string

        # Calculate the total amount from cart items
        total_amount = sum(float(item['price']) * int(item['quantity']) for item in cart.values())

        # Parse the data from the AJAX POST request (via JSON)
        try:
            data = json.loads(request.body)  # Data from frontend's submitShippingInfo() function
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid data format'}, status=400)

        try:
            # Create an order instance
            order = Order.objects.create(
                user=request.user,  # Assuming user is logged in
                total_amount=total_amount,
                shipping_full_name=data['full_name'],
                shipping_email_address=data['email_address'],
                shipping_phone_number=data['phone_number'],
                shipping_address=data['address'],
                shipping_country=data['country'],
                shipping_state=data['state'],
                shipping_zip_code=data['zip_code'],
                agreed_to_terms=data['agreed_to_terms'],
            )

            # Add products from cart to the order
            for item in cart.values():
                product = Product.objects.get(id=item['product_id'])
                order.products.add(product)

            # Clear the cart after saving the order
            request.session['cart'] = {}

            # Optionally, send a confirmation email or any other post-order action
            send_order_confirmation(order)

            # Return a success response
            return JsonResponse({
                'message': 'Order saved successfully!',
                'cart_json': cart_json  # Include cart_json in the response
            }, status=200)

        except KeyError as e:
            # Handle missing fields in the incoming data
            return JsonResponse({'error': f'Missing required field: {str(e)}'}, status=400)
        except Product.DoesNotExist:
            # Handle missing product IDs
            return JsonResponse({'error': 'Product not found in cart'}, status=400)
        except Exception as e:
            # Catch any other general errors
            return JsonResponse({'error': f'Error occurred: {str(e)}'}, status=500)

    else:
        # For GET request (initial checkout page load)
        cart = get_cart(request)
        cart_items_with_total = []
        total_amount = 0

        # Calculate the total price for each cart item and overall total
        for item in cart.values():
            item_total = float(item['price']) * int(item['quantity'])  # Ensure proper type conversion
            total_amount += item_total
            cart_items_with_total.append({**item, 'total': item_total})

        # Ensure cart_json is set for rendering the template
        cart_json = json.dumps(cart) if cart else "[]"  # Convert cart to JSON or empty JSON array

        # Pass the country and state choices to the template
        return render(request, 'checkout.html', {
            'cart_json': cart_json,  # Pass the JSON string to the template
            'cart': cart_items_with_total,
            'total_amount': total_amount,
            'COUNTRY_CHOICES': COUNTRY_CHOICES,
            'STATE_CHOICES': STATE_CHOICES,
        })


def thankyou(request):
    order_id = request.session.get('order_id')  # Get order_id from session

    if not order_id:
        # Handle the case where order_id is not found in session
        return render(request, 'thankyou.html', {'error': 'Order ID is missing or invalid.'})

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        # If order doesn't exist, show an error message or display a default "thank you" page
        return render(request, 'thankyou.html', {'error': 'Order not found.'})

    return render(request, 'thankyou.html', {'order': order})


def service(request):
    return render(request, 'service.html')


def gallery(request):
    return render(request, 'gallery.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Create a Contact instance and save it to the database
        contact = Contact(name=name, email=email, phone=phone, message=message, date=datetime.today())
        contact.save()

        return JsonResponse({"message": "Your message has been sent!"})

    return render(request, 'contact.html')


# GET: Fetch all orders
@api_view(['GET'])
def get_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


# GET: Fetch a single order by ID
@api_view(['GET'])
def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def create_order(request):
    print("Incoming request data:", request.data)  # Debugging incoming request data

    # Ensure 'cart_data' exists in the request data
    if 'cart_data' not in request.data:
        return Response({"detail": "Cart data is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Extract cart_data and other order details
    cart_data = request.data['cart_data']
    total_amount = request.data.get('total_amount', 0)

    # Validate that the cart_data is not empty
    if not cart_data:
        return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

    # Calculate the total amount from the cart_data if it's not provided
    calculated_total = 0
    processed_cart_data = []  # List to hold the processed data for the cart

    for item in cart_data:
        product_id = item.get('product_id')
        quantity = item.get('quantity', 0)

        if not product_id or not quantity:
            return Response({"detail": "Each item must have a valid product_id and quantity."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Fetch product details to calculate total (you may want to include price and quantity validation here)
        try:
            product = Product.objects.get(id=product_id)
            product_details = {
                'product_id': product.id,
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
                'total': product.price * quantity,
                'image': product.image.url if product.image else None
            }
            processed_cart_data.append(product_details)
            calculated_total += product.price * quantity
        except Product.DoesNotExist:
            return Response({"detail": f"Product with ID {product_id} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

    # If the provided total_amount does not match the calculated total, return an error
    if total_amount != calculated_total:
        return Response({"detail": "Total amount does not match calculated cart total."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Prepare data for the order
    order_data = {
        'cart_data': processed_cart_data,  # Use the processed cart data (serializable data)
        'total_amount': total_amount,
        'order_status': 'pending',  # Default status for new orders
    }

    # Include shipping address if available
    if 'shipping_address' in request.data:
        order_data.update(request.data['shipping_address'])

    # Now, create the serializer with the prepared order data
    serializer = OrderSerializer(data=order_data)

    # Check if the serializer is valid
    if serializer.is_valid():
        order = serializer.save()

        # Return the created order data as response
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print("Serializer errors:", serializer.errors)  # Debugging serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# PUT: Update an existing order by ID
@api_view(['PUT'])
def update_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderSerializer(order, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE: Delete an order by ID
@api_view(['DELETE'])
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



def update_order_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            status = data.get('status')

            # Ensure that both order_id and status are present
            if not order_id or not status:
                return JsonResponse({'error': 'Missing order_id or status'}, status=400)

            # Assuming you have an Order model, update the order status
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()

            return JsonResponse({'message': 'Order status updated successfully'}, status=200)

        except Exception as e:
            # Log the error or return it in the response for debugging purposes
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)