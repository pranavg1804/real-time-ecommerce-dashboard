import time
import random
from faker import Faker
import psycopg2

fake = Faker()

conn = psycopg2.connect(
    host="localhost",
    database="ecommerce",
    user="admin",
    password="admin123",
    port=5432
)

cursor = conn.cursor()

categories = ["Electronics", "Fashion", "Home", "Books", "Grocery"]
regions = ["North", "South", "East", "West"]
payments = ["UPI", "Credit Card", "Debit Card", "Cash"]

while True:
    product_category = random.choice(categories)
    product_name = fake.word()
    quantity = random.randint(1, 5)
    price = round(random.uniform(100, 5000), 2)
    region = random.choice(regions)
    payment_method = random.choice(payments)

    cursor.execute(
        """
        INSERT INTO orders
        (product_category, product_name, quantity, price, region, payment_method)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (product_category, product_name, quantity, price, region, payment_method)
    )

    conn.commit()
    print("Inserted order")

    time.sleep(5)
