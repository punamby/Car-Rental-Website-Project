import pymysql

# Connect to MySQL
try:
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='Abc@1234',
        database='ffcarrentals1',
        autocommit=True
    )
    print("Connected to MySQL database")
except pymysql.Error as error:
    print("Error connecting to MySQL database:", error)
    exit(1)

# Execute a query
try:
    with connection.cursor() as cursor:
        # Example query to retrieve data from a table
        query = "SELECT * FROM car_filters"
        cursor.execute(query)
        results = cursor.fetchall()

        # Process the query results
        for row in results:
            # Access the column values of each row
            column1 = row[0]
            column2 = row[1]
            column3 = row[2]
            column4 = row[3]

            # Do something with the retrieved data
            print("Column 1:", column1)
            print("Column 2:", column2)
            print("Column 3:", column3)
            print("Column 4:", column4)
except pymysql.Error as error:
    print("Error executing query:", error)

# Close the database connection
connection.close()
