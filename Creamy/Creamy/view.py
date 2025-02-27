from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Contact
from Home.models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import JsonResponse
from Home.forms import OrderForm
from django.http import HttpResponseRedirect
from django.conf import settings
import stripe
import re
from django.http import HttpResponse

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
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char in '!@#$%^&*()_+' for char in password)

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
                form.add_error('password1',
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
    # Calculate the total price
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
            product = Product.objects.get(id=item['product_id'])  # Get product by ID
            item['product'] = product  # Add the full product object to the item
            products_in_cart.append(item)  # Append this item to the products_in_cart list
            total_price += item['price'] * item['quantity']  # Add to the total price
        else:
            # If 'product_id' is missing, print a warning
            print(f"Warning: 'product_id' not found in item: {item}")

    # Render the cart page with the cart data and total price
    return render(request, 'cart.html', {
        'cart': cart,
        'total_price': total_price,
        'products_in_cart': products_in_cart
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

# Checkout view
def checkout(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            # Create the order
            order = form.save(commit=False)  # Don't save yet to modify before saving

            # Assign cart products to the order
            cart = get_cart(request)
            total_amount = sum(item['price'] * item['quantity'] for item in cart.values())
            order.total_amount = total_amount

            # Save the order
            order.save()

            # Add the products in the cart to the order
            for item in cart.values():
                product = Product.objects.get(id=item['product_id'])
                order.products.add(product)

            # Clear the cart after order creation
            request.session['cart'] = {}

            return redirect('thankyou')  # Redirect to a 'thank you' page after order is placed

    else:
        form = OrderForm()

    return render(request, 'checkout.html', {'form': form})


def thankyou(request):
    # Get the most recent order
    order = Order.objects.latest('created_at')  # Fetch the latest order by creation date

    # Pass the order to the 'thankyou.html' template
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

def order(request):
    if request.method == 'POST':
        print("POST request received")  # This will print in your console when the form is submitted
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save()  # Save the form and return the saved order
            print("Order saved:", order)  # This will print the saved order to the console for debugging
            return HttpResponseRedirect('/thankyou/')  # Try using a hardcoded URL as a test
        else:
            print("Form errors:", form.errors)  # Print form errors to the console if validation fails
    else:
        print("GET request received")  # This will print if the page is accessed without submitting the form

    return render(request, 'checkout.html', {'form': form})