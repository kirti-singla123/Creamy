"""
URL configuration for Creamy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .import view


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', view.home, name='home'),
    path('login/', view.login_view, name='login'),
    path('signup/', view.signup_view, name='signup'),
    path('logout/', view.logout_view, name='logout'),
    path('home/', view.home, name='home'),
    path('about/', view.about, name='about'),
    path('product/', view.product_list, name='product'),
    path('cart/', view.cart, name='cart'),
    path('cart/<int:id>/', view.cart, name='cart'),
    path('service/', view.service, name='service'),
    path('gallery/', view.gallery, name='gallery'),
    path('contact/', view.contact, name='contact'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
