from django.shortcuts import render, redirect, get_object_or_404
from Home.models import Product, Contact
from Home.models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import JsonResponse
from Home.forms import OrderForm
from django.http import HttpResponseRedirect
from django.http import HttpResponse


# password for test user: HARRYdonal

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

# View for Sign Up
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful sign-up
        else:
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
    cart = get_cart(request)

    # Get the product by ID or return a 404 if it does not exist
    product = get_object_or_404(Product, id=product_id)

    # Convert price to float before storing in session
    price = float(product.price)

    # If the product is already in the cart, increment the quantity
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1
    else:
        cart[str(product.id)] = {
            'name': product.name,
            'price': price,
            'quantity': 1,
            'image': product.image.name,
        }

    # Save the cart back into session
    request.session['cart'] = cart

    # Redirect to the cart page
    return redirect('cart')

# Your cart view
def cart(request):
    cart = get_cart(request)

    # Calculate the total price
    total_price = sum(item['price'] * item['quantity'] for item in cart.values())

    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

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
    if request.method == 'POST':  # When the form is submitted
        form = OrderForm(request.POST)  # Create the form with POST data

        if form.is_valid():  # Check if the form is valid
            # If the form is valid, save the data to the database and redirect
            order = form.save()
            return redirect('thankyou')  # Redirect to a thank you page or another success page
        else:
            # If the form is not valid, print the errors
            print(form.errors)  # This will print the form errors to the console

    else:
        form = OrderForm()  # If the request method is not POST, just display an empty form

    return render(request, 'checkout.html', {'form': form})  # Return the form to the template

def thankyou(request):
    return render(request, 'thankyou.html')

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