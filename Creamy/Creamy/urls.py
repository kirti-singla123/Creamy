"""
URL configuration for Creamy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views. home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from Creamy import view


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', view.home, name='home'),
    path('login/', view.login_view, name='login'),
    path('signup/', view.signup_view, name='signup'),
    path('logout/', view.logout_view, name='logout'),
    path('home/', view.home, name='home'),
    path('about/', view.about, name='about'),
    path('product/', view.product_list, name='product'),
    path('add_to_cart/<int:product_id>/', view.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', view.remove_from_cart, name='remove_from_cart'),
    path('decrease-quantity/<int:product_id>/', view.decrease_quantity, name='decrease_quantity'),
    path('cart/increase/<int:product_id>/', view.increase_quantity, name='increase_quantity'),
    path('cart/', view.cart, name='cart'),
    path('service/', view.service, name='service'),
    path('gallery/', view.gallery, name='gallery'),
    path('contact/', view.contact, name='contact'),
    path('checkout/', view.checkout, name='checkout'),
    path('api/orders/', view.get_orders, name='get_orders'),  # GET all orders
    path('api/orders/<int:order_id>/', view.get_order, name='get_order'),  # GET a specific order
    path('api/orders/create/', view.create_order, name='create_order'),  # POST create order
    path('api/orders/update/<int:order_id>/', view.update_order, name='update_order'),  # PUT update order
    path('api/orders/delete/<int:order_id>/', view.delete_order, name='delete_order'),  # DELETE delete order
    path('api/update_order_status/', view.update_order_status, name='update_order_status'),
    path('thankyou/', view.thankyou, name='thankyou'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
