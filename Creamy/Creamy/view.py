# created by kirti
from django.shortcuts import render, redirect
from Home.models import Product
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from datetime import datetime
from Home.models import Contact
from django.http import JsonResponse

# password for test user : HARRYdonal

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
        print("POST data:", request.POST)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful sign-up
        else:
            print("Form is not valid")
            print(form.errors)  # This will print out any form errors
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
    return render(request, 'product.html',{'products': products})


# Add to Cart view
def add_to_cart(request, product_id):
    # Check if cart exists in session
    cart = request.session.get('cart', {})

    # Get the product by ID
    product = Product.objects.get(id=product_id)

    # Convert price to float before storing in session
    price = float(product.price)

    # If the product is already in the cart, increment the quantity
    if str(product.id) in cart:
        cart[str(product.id)]['quantity'] += 1
    else:
        cart[str(product.id)] = {
            'name': product.name,
            'price': price,  # Store price as float
            'quantity': 1,
            'image': product.image.name,
        }

    # Save the cart back into session
    request.session['cart'] = cart

    # Redirect to the cart page
    return redirect('cart')


# Your cart view
def cart(request):
    # Retrieve the cart from the session
    cart = request.session.get('cart', {})

    # Calculate the total price
    total_price = 0
    for item in cart.values():
        total_price += item['price'] * item['quantity']  # Multiply price by quantity for each item

    # Pass cart and total price to the template
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})



# Define the checkout view
def checkout(request):
    # You can add logic here for the checkout process if needed
    return render(request, 'checkout.html')



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
