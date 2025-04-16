import psycopg2
import threading
import time
import random
import hashlib
from faker import Faker
import os

# Load credentials securely
conn = psycopg2.connect(
    database=os.getenv("DB_NAME", "pinnacledb"),
    user=os.getenv("DB_USER", "postgres"),
    host=os.getenv("DB_HOST", "your-db-host.amazonaws.com"),
    port=os.getenv("DB_PORT", "5432"),
    password=os.getenv("DB_PASSWORD", "your-secret-password")
)

speed = 150
fake = Faker()

def generateCustomer(speed=speed):
    n = random.choice([1, 2, 3])
    time.sleep((600 * n) / speed)

    custID = 'C' + str(int(time.time()))[-8:]
    custName = fake.name()
    custAdd = fake.address()

    cursor = conn.cursor()
    query = """INSERT INTO ECART.CUSTOMER (CUSTID, CUSTNAME, CUSTADD) VALUES (%s,%s,%s)"""
    cursor.execute(query, (custID, custName, custAdd))
    conn.commit()

    print("Inserted customer:", custID)

def small_hash(input_string):
    return hashlib.sha256(input_string.encode()).hexdigest()[:10]

def generateProductsAndStores():
    time.sleep((300 * random.choice([2.5, 3.5, 4.5])) / speed)

    adjective = random.choice(["Premium", "Smart", "Eco", "Pro"])
    noun = random.choice(["Laptop", "Speaker", "Printer", "Camera"])
    productName = f"{adjective} {noun}"
    productID = int(str(int(time.time()))[4:10])
    productPrice = round(random.uniform(100, 2000), 2)

    storeName = f"{random.choice(['Tech', 'Digital'])} & {random.choice(['Hub', 'Plaza'])}"
    storeID = small_hash(storeName)
    storeAdd = fake.address()

    cursor = conn.cursor()
    cursor.execute("""INSERT INTO ECART.PRODUCTINFO (PRODUCTID, PRODUCTNAME, PRODCAT, STOREID, PRODUCTPRICE) 
                      VALUES (%s, %s, %s, %s, %s)""", 
                   (productID, productName, noun, storeID, productPrice))

    cursor.execute("""INSERT INTO ECART.STOREINFO (STOREID, STORENAME, STOREADD) VALUES (%s, %s, %s)""", 
                   (storeID, storeName, storeAdd))
    conn.commit()

    print("Inserted product and store:", productID, storeID)

def generateOrderFact():
    time.sleep((100 * random.choice([0.5, 1, 1.5])) / speed)

    cursor = conn.cursor()
    cursor.execute("SELECT CUSTID FROM ECART.CUSTOMER ORDER BY RANDOM() LIMIT 1")
    custid = cursor.fetchone()

    cursor.execute("SELECT PRODUCTID FROM ECART.PRODUCTINFO ORDER BY RANDOM() LIMIT 1")
    productid = cursor.fetchone()

    if custid and productid:
        cursor.execute("""INSERT INTO ECART.FACT_ORDER (CUSTID, PRODUCTID) VALUES (%s, %s)""", (custid[0], productid[0]))
        conn.commit()
        print("Inserted order")

def updateRecords():
    time.sleep((100 * random.choice([15, 20, 50])) / speed)

    cursor = conn.cursor()
    cursor.execute("SELECT CUSTID FROM ECART.CUSTOMER ORDER BY RANDOM() LIMIT 1")
    custid = cursor.fetchone()

    cursor.execute("SELECT PRODUCTID FROM ECART.PRODUCTINFO ORDER BY RANDOM() LIMIT 1")
    productid = cursor.fetchone()

    if custid:
        cursor.execute("""UPDATE ECART.CUSTOMER SET CUSTADD = 
            CASE WHEN CUSTADD ~ '_v[0-9]$' 
            THEN CONCAT(LEFT(CUSTADD, LENGTH(CUSTADD)-1), CAST(RIGHT(CUSTADD, 1) AS INTEGER)+1) 
            ELSE CONCAT(CUSTADD, '_v1') END 
            WHERE CUSTID = %s""", (custid[0],))

    if productid:
        cursor.execute("""UPDATE ECART.PRODUCTINFO SET PRODUCTNAME = 
            CASE WHEN PRODUCTNAME ~ '_v[0-9]$' 
            THEN CONCAT(LEFT(PRODUCTNAME, LENGTH(PRODUCTNAME)-1), CAST(RIGHT(PRODUCTNAME, 1) AS INTEGER)+1) 
            ELSE CONCAT(PRODUCTNAME, '_v1') END 
            WHERE PRODUCTID = %s""", (productid[0],))
    
    conn.commit()
    print("Updated customer and product record")

def deleteRecords():
    time.sleep((100 * random.choice([25, 30, 45])) / speed)

    cursor = conn.cursor()
    cursor.execute("SELECT ORDERID FROM ECART.FACT_ORDER ORDER BY RANDOM() LIMIT 1")
    orderid = cursor.fetchone()

    if orderid:
        cursor.execute("DELETE FROM ECART.FACT_ORDER WHERE ORDERID = %s", (orderid[0],))
        conn.commit()
        print("Deleted order", orderid[0])
