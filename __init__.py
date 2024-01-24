import pymysql


class FFCARRENTALS1:
    def __init__(self):
        self.con = None
        self.cur = None
        self.connect_to_database()

    def connect_to_database(self):
        try:
            self.con = pymysql.connect(
                host='localhost',
                port=3306,
                user='root',
                password='Abc@1234',
                database='ffcarrentals1'
            )
            self.cur = self.con.cursor()
            print("Connected to the database")
        except pymysql.Error as error:
            print("Error connecting to the database:", error)


    def view_car_filters(self):
        query = "SELECT * FROM car_filters"
        self.cur.execute(query)
        car_filters = self.cur.fetchall()

        print("Car Filters")
        print("FilterID\tVehicleType\tTransmission\tMileage\tFuel")
        for car_filter in car_filters:
            filter_id, vehicle_type, transmission, mileage, fuel = car_filter
            print(f"{filter_id}\t\t{vehicle_type}\t\t{transmission}\t\t{mileage}\t\t{fuel}")

    def view_customers(self):
        query = "SELECT * FROM customers"
        self.cur.execute(query)
        customers = self.cur.fetchall()

        print("Customers")
        print("FirstName\tLastName\tMobile_number\tEmail\t\tPassword")
        for customer in customers:
            first_name, last_name, mobile_number, email, password = customer
            print(f"{first_name}\t\t{last_name}\t\t{mobile_number}\t\t{email}\t{password}")

    def view_locations(self):
        query = "SELECT * FROM locations"
        self.cur.execute(query)
        locations = self.cur.fetchall()

        print("Locations")
        print("LocationID\tLocationName")
        for location in locations:
            location_id, location_name = location
            print(f"{location_id}\t\t{location_name}")

    def view_rentals(self):
        query = "SELECT * FROM rentals"
        self.cur.execute(query)
        rentals = self.cur.fetchall()

        print("Rentals")
        print("RentalID\tCarID\tLocationID\tCustomerID\tPickupLocationID\tDropoffLocationID\tPickupDate\tPickupTime\tDropoffDate\tDropoffTime\tTotalCost")
        for rental in rentals:
            rental_id, car_id, location_id, customer_id, pickup_location_id, dropoff_location_id, \
            pickup_date, pickup_time, dropoff_date, dropoff_time, total_cost = rental
            print(f"{rental_id}\t\t{car_id}\t\t{location_id}\t\t{customer_id}\t\t{pickup_location_id}\t\t{dropoff_location_id}\t\t{pickup_date}\t{pickup_time}\t{dropoff_date}\t{dropoff_time}\t{total_cost}")

    def store_data_in_database(self, data):
        first_name = data['first_name']
        last_name = data['last_name']
        mobile_number = data['mobile_number']
        email = data['email']
        password = data['password']

        # Insert the data into the database
        query = "INSERT INTO customers (FirstName, LastName, Mobile_number, Email, Password) VALUES (%s, %s, %s, %s, %s)"
        values = (first_name, last_name, mobile_number, email, password)
        self.cur.execute(query, values)
        self.con.commit()

        # Print a success message
        print("Data stored in the database.")

# Instantiate the FFCARRENTALS1 class
car_rentals = FFCARRENTALS1()

