# 🍦 Creamy – Ice Cream eCommerce Website

**Creamy** is a user-friendly online store built with Django, made especially for ice cream lovers. From classic chocolate to fruity sorbets, it lets users easily browse, choose, and buy their favorite ice cream.

With a smooth shopping experience, **Creamy** offers features like user login, a shopping cart, and a responsive design built with Bootstrap, making the website easy to use on any device.


## 🚀 Features

- **User Registration & Login:** Users can create accounts, log in, and manage their profiles.

- **Product Browsing:** Browse through a variety of ice cream flavors with images and descriptions. 

- **Add to Cart & Cart Management:**
  - Add products to the cart with a single click, view items in your cart, change quantities, remove products, and see the total price in real-time. 

- **Checkout Process:**
  - The checkout system is designed to be simple and intuitive, allowing users to review their order, fill in their shipping details, and proceed with ease.

- **Responsive Design:**
  - The website uses Bootstrap to ensure it’s fully responsive, providing a smooth experience on all devices, from desktops to mobile phones and tablets.

- **Contact Us Feature:** 
  - Users can easily get in touch for support or inquiries via the "Contact Us" page.
  - This includes a simple contact form where users can submit their messages directly from the website.
  - For further assistance, users can also find contact information like email, phone, and social media links in the footer.

- **Secure Checkout (Future Integration):**
  - Designed to support secure payment methods like credit cards or PayPal (integration coming soon), ensuring safe transactions for users.

- **Admin Panel for Product Management:**
  - Admin users can easily manage ice cream products, including adding new flavors, editing descriptions, changing prices, uploading images, and removing outdated products.
  - Admins can also monitor inventory levels, ensuring the store is always stocked with the best ice cream.

- **Order Tracking & Management:** 
  - Admins can view all user orders, including detailed information such as:
    - User ID, product info (name, quantity), and price.
    - The order status can be updated to "Shipped", "Delivered", or "Cancelled".
  - This helps admins track the status of each order

  - **Interactive Elements:** 
  - JavaScript is used to dynamically update cart totals and handle order placement, ensuring a smooth and interactive checkout experience.

 -**Order Management API:** 
  - The project includes a RESTful API to manage orders, with the following endpoints:
    - **GET /api/orders/**: Retrieve all orders.
    - **GET /api/orders/<order_id>/**: Retrieve a specific order by its ID.
    - **POST /api/orders/create/**: Create a new order.
    - **PUT /api/orders/update/<order_id>/**: Update an existing order.
    - **DELETE /api/orders/delete/<order_id>/**: Delete an order by its ID.
    - **POST /api/update_order_status/**: Update the status of an order (e.g., "Shipped", "Delivered", "Cancelled").
 
 - **PayPal Payment Gateway Integration (Sandbox):** 
  - The website integrates PayPal's Sandbox environment for secure and seamless payment processing during testing, allowing users to complete their purchases safely before going live.

- **Secure User Authentication:**
  - Built with Django's secure authentication system, ensuring that user data, including passwords, are kept safe.

- **Easy-to-Use Interface:** 
  - Clean, modern design with a user-friendly interface that makes shopping and navigating the site a breeze for all users.
    

## 🛠️ Tech Stack

- **Language:** Python
- **Backend:** Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Database:** SQLite
- **Payment Integration:** PayPal (Sandbox)
- **API:** Django REST Framework


## 🚀 Live Demo

You can check out the fully functional Creamy eCommerce website here: soon
👉 Live Site

No need to install anything locally — just click the link and explore the creamy goodness! 🍨

## 📸 Screenshots

![Home Page](![image](https://github.com/user-attachments/assets/dcf39748-76dc-4766-96a9-4cd122c3c85c)
![Product Page](![image](https://github.com/user-attachments/assets/932cb9a2-732c-4e75-883d-ca0afaa8b471)
![Cart Page](![image](https://github.com/user-attachments/assets/ce1fdcb4-5437-4b5c-8dc2-8c3848c6e705)
![Checkout Page](![image](https://github.com/user-attachments/assets/4734fc55-551e-445a-894f-383ef1d09a33)
![Contact Us Page] (![image](https://github.com/user-attachments/assets/a5093bb9-bdd0-4b1c-8d33-e95b9d07d27e)

## 🧑‍💻 Author

- **Name:** Kirti Singla  
- **GitHub:** [@kirti-singla123](https://github.com/kirti-singla123)
- **LinkedIn:** www.linkedin.com/in/kirti-singla-web-dev


