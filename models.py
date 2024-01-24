from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser, Group, Permission


class Locations(models.Model):
    objects = None
    LocationID = models.AutoField(primary_key=True)
    LocationName = models.CharField(max_length=100)
    pickup_location_id = models.PositiveIntegerField()
    drop_location_id = models.PositiveIntegerField()

    def __str__(self):
        return self.LocationName


class Rentals(models.Model):
    pickup_location = models.ForeignKey(
        Locations, on_delete=models.CASCADE, related_name='pickup'
    )
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    drop_location = models.ForeignKey(
        Locations, on_delete=models.CASCADE, related_name='drop'
    )
    drop_date = models.DateField()
    drop_time = models.TimeField()

    def __str__(self):
        return f'Rental ({self.pk})'


class Customer(models.Model):
    objects = None
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    rentals = models.ManyToManyField(Rentals, related_name='customers')

    def __str__(self):
        return f'Customer: {self.first_name} {self.last_name}'


class Vehicle(models.Model):
    objects = None
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Transmission(models.Model):
    objects = None
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Mileage(models.Model):
    objects = None
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class User(models.Model):
    objects = None
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Fuel(models.Model):
    objects = None
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CarFilters(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    transmission = models.ForeignKey(Transmission, on_delete=models.CASCADE)
    mileage = models.ForeignKey(Mileage, on_delete=models.CASCADE)
    fuel = models.ForeignKey(Fuel, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Filter ID: {self.pk} - {self.vehicle}, {self.transmission}, {self.mileage}, {self.fuel}"


class ffcarrentals1_booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    transmission = models.CharField(max_length=50)
    fuel = models.CharField(max_length=50)

    def __str__(self):
        return f"Booking {self.user} - Vehicle: {self.vehicle}, User: {self.user.username}, Price: {self.price}, transmission: {self.transmission}, fuel: {self.fuel}"


class Quote(models.Model):
    VEHICLE_CHOICES = (
        ('SUV', 'SUV'),
        ('SEDAN', 'SEDAN'),
        ('LUXURY', 'LUXURY'),
    )

    TRANSMISSION_CHOICES = (
        ('AUTOMATIC', 'AUTOMATIC'),
        ('MANUAL', 'MANUAL'),
    )

    MILEAGE_CHOICES = (
        ('LIMITED', 'LIMITED'),
        ('UNLIMITED', 'UNLIMITED'),
    )

    FUEL_CHOICES = (
        ('PETROL', 'PETROL'),
        ('DIESEL', 'DIESEL'),
        ('ELECTRIC', 'ELECTRIC'),
    )

    vehicle = models.CharField(max_length=50, choices=VEHICLE_CHOICES)
    transmission = models.CharField(max_length=50, choices=TRANSMISSION_CHOICES)
    mileage = models.CharField(max_length=50, choices=MILEAGE_CHOICES)
    fuel = models.CharField(max_length=50, choices=FUEL_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehicle} - {self.transmission} - {self.mileage} - {self.fuel}"

class AdminManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not username:
            raise ValueError("The username must be set")
        if not email:
            raise ValueError("The email must be set")

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class AdminUser(AbstractUser):
    # Custom fields and methods for the AdminUser model

    class Meta:
        # Add a unique app_label to avoid conflicts with the built-in User model
        app_label = 'ffcarrentals1'

    # Add or change the related_name arguments for groups and user_permissions fields
    groups = models.ManyToManyField(Group, blank=True, related_name='admin_users')
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name='admin_users')

class ffcarrentals1_vehicle(models.Model):
    vehicle_type = models.CharField(max_length=100)
    transmission = models.CharField(max_length=50)
    fuel = models.CharField(max_length=50)
    mileage = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Vehicle: {self.vehicle_type}, Transmission: {self.transmission}, Fuel: {self.fuel}, Mileage: {self.mileage}, Price: {self.price}"