from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.checks import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import CarFilters, Vehicle
from .models import Customer, Locations
from .models import ffcarrentals1_booking
from .forms import AdminRegistrationForm, AdminLoginForm
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.views import PasswordResetView

def home_view(request):
    if request.method == 'POST':
        selected_pickup_location_id = request.POST.get('user-pickup')
        selected_drop_location_id = request.POST.get('user-drop')
        locations = Locations.objects.all()
        return render(request, 'home.html',
                      {'locations': locations, 'selected_pickup_location_id': selected_pickup_location_id,
                       'selected_drop_location_id': selected_drop_location_id})

    if request.method == 'GET':
        selected_pickup_location_id = request.GET.get('user-pickup')
        selected_pickup_date_str = request.GET.get('user-pickup-date')
        selected_pickup_time_str = request.GET.get('user-pickup-time')
        selected_drop_location_id = request.GET.get('user-drop')
        selected_drop_date_str = request.GET.get('user-drop-date')
        selected_drop_time_str = request.GET.get('user-drop-time')

        locations = Locations.objects.all()

        if selected_pickup_date_str and selected_pickup_time_str:
            selected_pickup_datetime = datetime.strptime(selected_pickup_date_str + selected_pickup_time_str,
                                                         '%Y-%m-%d%H:%M')
        else:
            selected_pickup_datetime = None

        if selected_drop_date_str and selected_drop_time_str:
            selected_drop_datetime = datetime.strptime(selected_drop_date_str + selected_drop_time_str, '%Y-%m-%d%H:%M')
        else:
            selected_drop_datetime = None

        return render(request, 'home.html',
                      {'locations': locations, 'selected_pickup_location_id': selected_pickup_location_id,
                       'selected_pickup_datetime': selected_pickup_datetime,
                       'selected_drop_location_id': selected_drop_location_id,
                       'selected_drop_datetime': selected_drop_datetime})

    locations = Locations.objects.all()
    return render(request, 'home.html', {'locations': locations})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('user-email')
        password = request.POST.get('user-password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['user-email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Handle case when user with provided email does not exist
            return render(request, 'forgot_password.html', {'error_message': 'User with this email does not exist.'})

        token = default_token_generator.make_token(user)
        reset_password_link = request.build_absolute_uri(
            reverse('reset_password', kwargs={'user_id': user.id, 'token': token})
        )

        # Send reset password email to the user
        send_mail(
            'Reset Your Password',
            f'Click the following link to reset your password: {reset_password_link}',
            'noreply@example.com',
            [email],
            fail_silently=False,
        )

        # Redirect to a success page or display a success message
        return render(request, 'password_reset_sent.html')

    return render(request, 'forgot-password.html')

def reset_password_view(request):
    return PasswordResetView.as_view(
        template_name='reset_password.html',
        email_template_name='reset_password_email.html',
        success_url='password_reset_done'
    )(request)

def about_view(request):
    return render(request, 'about.html')


@login_required()
def addons_view(request):
    return render(request, 'addons.html')


@login_required
def payment_view(request):
    auth_user = request.user

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        vehicle = request.POST.get('vehicle')
        transmission = request.POST.get('transmission')
        fuel = request.POST.get('fuel')
        price = request.POST.get('price')

        if auth_user.is_authenticated:
            booking = ffcarrentals1_booking.objects.create(user_id=auth_user.id, vehicle=vehicle, price=price,
                                                           transmission=transmission, fuel=fuel)

            booking.save()
            return redirect('process-payment.html')
    return render(request, 'payment.html')


@login_required
def bookings_view(request):
    auth_user = request.user
    bookings = ffcarrentals1_booking.objects.filter(user_id=auth_user.id)

    if request.method == 'POST':
        booking_id = request.POST.get('booking_id')
        try:
            booking = ffcarrentals1_booking.objects.get(id=booking_id, user_id=auth_user.id)
            booking.delete()
            return redirect('bookings.html')
        except ffcarrentals1_booking.DoesNotExist:
            return redirect('bookings.html')

    booking_data = [
        {
            'id': booking.id,
            'vehicle': booking.vehicle,
            'fuel': booking.fuel,
            'transmission': booking.transmission,
            'price': booking.price
        }
        for booking in bookings
    ]

    user_data = {
        'username': auth_user.first_name,
        'email': auth_user.email,
    }

    return render(request, 'bookings.html', {'booking_data': booking_data, 'user_data': user_data})


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(ffcarrentals1_booking, id=booking_id)
    booking.delete()
    return redirect(request, 'bookings.html')


@login_required
def process_payment_view(request):
    auth_user = request.user

    if request.method == 'POST':
        vehicle = request.POST.get('vehicle')
        price = request.POST.get('price')
        transmission = request.POST.get('transmission')
        fuel = request.POST.get('fuel')

        if auth_user.is_authenticated:
            if price:
                booking = ffcarrentals1_booking.objects.create(
                    user_id=auth_user.id,
                    vehicle=vehicle,
                    price=price,
                    transmission=transmission,
                    fuel=fuel
                )
                booking.save()
            else:
                return HttpResponse('Invalid price value')
            return redirect('process-payment.html')
    return render(request, 'process-payment.html')


@login_required()
def logout_view(request):
    logout(request)
    return render(request, 'logout.html')


@login_required()
def filters_view(request):
    vehicle_type = request.GET.get('vehicle_type')
    transmission = request.GET.get('transmission')
    mileage = request.GET.get('mileage')
    fuel = request.GET.get('fuel')
    price = request.GET.get('price')

    quotes = [
        {'vehicle': {'id': 1, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 105},
        {'vehicle': {'id': 2, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 110},
        {'vehicle': {'id': 3, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 105},
        {'vehicle': {'id': 4, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 115},
        {'vehicle': {'id': 5, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 120},
        {'vehicle': {'id': 6, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 125},
        {'vehicle': {'id': 7, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 100},
        {'vehicle': {'id': 8, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 105},
        {'vehicle': {'id': 9, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 110},
        {'vehicle': {'id': 10, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 125},
        {'vehicle': {'id': 11, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 130},
        {'vehicle': {'id': 12, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 135},
        {'vehicle': {'id': 13, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 135},
        {'vehicle': {'id': 14, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 105},
        {'vehicle': {'id': 15, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 115},
        {'vehicle': {'id': 16, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 125},
        {'vehicle': {'id': 17, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 125},
        {'vehicle': {'id': 18, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 120},
        {'vehicle': {'id': 19, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 120},
        {'vehicle': {'id': 20, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 120},
        {'vehicle': {'id': 21, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 125},
        {'vehicle': {'id': 22, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 120},
        {'vehicle': {'id': 23, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 125},
        {'vehicle': {'id': 24, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 115},
        {'vehicle': {'id': 25, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 105},
        {'vehicle': {'id': 26, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 120},
        {'vehicle': {'id': 27, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 110},
        {'vehicle': {'id': 28, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 110},
        {'vehicle': {'id': 29, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 115},
        {'vehicle': {'id': 30, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 125},
        {'vehicle': {'id': 31, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 135},
        {'vehicle': {'id': 32, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 140},
        {'vehicle': {'id': 33, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 140},
        {'vehicle': {'id': 34, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 145},
        {'vehicle': {'id': 35, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 150},
        {'vehicle': {'id': 36, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
         'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 150}
    ]

    filtered_quotes = []
    for quote in quotes:
        if vehicle_type and quote['vehicle']['vehicle'] != vehicle_type:
            continue
        if transmission and quote['transmission'] != transmission:
            continue
        if mileage and quote['mileage'] != mileage:
            continue
        if fuel and quote['fuel'] != fuel:
            continue
        if price and quote['price'] != price:
            continue
        filtered_quotes.append(quote)

    context = {'quotes': filtered_quotes}
    return render(request, 'filters.html', context)


@login_required()
def quote_view(request):
    if request.method == 'GET':
        vehicle = request.GET.get('vehicle')
        transmission = request.GET.get('transmission')
        mileage = request.GET.get('mileage')
        fuel = request.GET.get('fuel')
        price = request.GET.get('price')

        quotes = [
            {'vehicle': {'id': 1, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 115},
            {'vehicle': {'id': 2, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 105},
            {'vehicle': {'id': 3, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 115},
            {'vehicle': {'id': 4, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 120},
            {'vehicle': {'id': 5, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 125},
            {'vehicle': {'id': 6, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 110},
            {'vehicle': {'id': 7, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 105},
            {'vehicle': {'id': 8, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 110},
            {'vehicle': {'id': 9, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 115},
            {'vehicle': {'id': 10, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 120},
            {'vehicle': {'id': 11, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 125},
            {'vehicle': {'id': 12, 'vehicle': 'SUV', 'image_url': 'static/images/login.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 115},
            {'vehicle': {'id': 13, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 110},
            {'vehicle': {'id': 14, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 110},
            {'vehicle': {'id': 15, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 125},
            {'vehicle': {'id': 16, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 125},
            {'vehicle': {'id': 17, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 120},
            {'vehicle': {'id': 18, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 110},
            {'vehicle': {'id': 19, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 120},
            {'vehicle': {'id': 20, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 115},
            {'vehicle': {'id': 21, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 125},
            {'vehicle': {'id': 22, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 120},
            {'vehicle': {'id': 23, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 120},
            {'vehicle': {'id': 24, 'vehicle': 'SEDAN', 'image_url': 'static/images/home.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 115},
            {'vehicle': {'id': 25, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 135},
            {'vehicle': {'id': 26, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 130},
            {'vehicle': {'id': 27, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 130},
            {'vehicle': {'id': 28, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 140},
            {'vehicle': {'id': 29, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 130},
            {'vehicle': {'id': 30, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'AUTOMATIC', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 135},
            {'vehicle': {'id': 31, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'PETROL', 'price': 135},
            {'vehicle': {'id': 32, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'DIESEL', 'price': 140},
            {'vehicle': {'id': 33, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'LIMITED', 'fuel': 'ELECTRIC', 'price': 140},
            {'vehicle': {'id': 34, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'PETROL', 'price': 145},
            {'vehicle': {'id': 35, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'DIESEL', 'price': 140},
            {'vehicle': {'id': 36, 'vehicle': 'LUXURY', 'image_url': 'static/images/signup.jpg'},
             'transmission': 'MANUAL', 'mileage': 'UNLIMITED', 'fuel': 'ELECTRIC', 'price': 145}

        ]

        filtered_quotes = []
        for quote in quotes:
            if vehicle and quote['vehicle']['vehicle'] != vehicle:
                continue
            if transmission and quote['transmission']['transmission'] != transmission:
                continue
            if mileage and quote['mileage']['mileage'] != mileage:
                continue
            if fuel and quote['fuel']['fuel'] != fuel:
                continue
            if fuel and quote['price']['price'] != price:
                continue
            filtered_quotes.append(quote)

        context = {
            'quotes': filtered_quotes,
            'selected_vehicle_type': vehicle,
            'selected_transmission': transmission,
            'selected_mileage': mileage,
            'selected_fuel': fuel,
            'selected_price': price,
        }
        return render(request, 'quote.html', context)
    return render(request, 'quote.html')


def signup_view(request):
    try:
        locations = Locations.objects.all()
        car_filters = CarFilters.objects.all()

        if request.method == 'POST':
            first_name = request.POST.get('user-first-name')
            last_name = request.POST.get('user-last-name')
            mobile_number = request.POST.get('user-mobile-number')
            email = request.POST.get('user-email')
            password = request.POST.get('user-password')

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=email,
                email=email,
                password=password
            )

            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                mobile_number=mobile_number,
                email=email,
                password=password
            )

            selected_pickup_location_id = request.POST.get('user-pickup')
            selected_drop_location_id = request.POST.get('user-drop')
            customer.pickup_location = Locations.objects.get(LocationID=selected_pickup_location_id)
            customer.drop_location = Locations.objects.get(LocationID=selected_drop_location_id)
            customer.save()
            return redirect('home.html')
        return render(request, 'signup.html', {'locations': locations,
                                               'car_filters': car_filters})

    except ObjectDoesNotExist:
        return redirect('home.html')
        return render(request, 'signup.html')


def admin_register_view(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin registered successfully. Please log in.')
            return redirect('admin_login.html')
    else:
        form = AdminRegistrationForm()
    return render(request, 'admin_register.html', {'form': form})


def admin_login_view(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('admin-email')
            password = form.cleaned_data.get('admin-password')
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_admin:
                login(request, user)
                return redirect('admin_home')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = AdminLoginForm()
    return render(request, 'admin_login.html', {'form': form})


def admin_logout_view(request):
    logout(request)
    return redirect('admin_logout.html')


def admin_home_view(request):
    return render(request, 'admin_home.html')


def add_vehicle_view(request):
    if request.method == 'POST':
        vehicle_type = request.POST.get('vehicle-type')
        transmission = request.POST.get('transmission')
        fuel = request.POST.get('fuel')
        mileage = request.POST.get('mileage')
        price = request.POST.get('price')

        vehicle = Vehicle.objects.create(
            vehicle_type=vehicle_type,
            transmission=transmission,
            fuel=fuel,
            mileage=mileage,
            price=price
        )

        return redirect('admin_home.html')

    return render(request, 'admin_home.html')
