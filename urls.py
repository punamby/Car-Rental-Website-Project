from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('home.html', views.home_view, name='home'),
    path('login.html', views.login_view, name='login'),
    path('logout.html', views.logout_view, name='logout'),
    path('about.html', views.about_view, name='about'),
    path('signup.html', views.signup_view, name='signup'),
    path('forgot-password.html', views.forgot_password_view, name='forgot-password'),
    path('reset_password.html', views.reset_password_view, name='reset_password'),
    path('quote.html', views.quote_view, name='quote'),
    path('filters.html', views.filters_view, name='filters'),
    path('addons.html', views.addons_view, name='addons'),
    path('payment.html', views.payment_view, name='payment'),
    path('bookings.html', views.bookings_view, name='bookings'),
    path('process-payment.html', views.process_payment_view, name='process-payment'),
    path('accounts/login/login.html', views.login_view, name='login'),
    path('accounts/login/payment.html', views.payment_view, name='payment'),
    path('bookings/cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('admin_register.html', views.admin_register_view, name='admin_register'),
    path('admin_login.html', views.admin_login_view, name='admin_login'),
    path('admin_home.html', views.admin_home_view, name='admin_home'),
    path('add_vehicle', views.add_vehicle_view, name='add_vehicle')
]



