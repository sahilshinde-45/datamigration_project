import csv
import time
import random
import boto3
import os
from faker import Faker

fake = Faker()

# Replace hardcoded dictionary with an external configuration if needed
PRODUCT_DICT = {
    'Laptop': 'Electronics',
    'Desktop Computer': 'Electronics',
    'Smartphone': 'Electronics',
    'T-shirt': 'Clothing',
    'Jeans': 'Clothing',
    'Dress': 'Clothing',
    'Sofa': 'Home Decor',
    'Coffee Table': 'Home Decor',
    'Bedding Set': 'Home Decor',
    'Action Figure': 'Toys',
    'Board Game': 'Toys',
    'Building Blocks': 'Toys',
    'Running Shoes': 'Sports',
    'Yoga Mat': 'Sports',
    'Basketball': 'Sports',
    'Novel': 'Books',
    'Cookbook': 'Books',
    'Art Book': 'Books',
    'Lipstick': 'Beauty',
    'Shampoo': 'Beauty',
    'Perfume': 'Beauty',
    'Milk': 'Grocery',
    'Bread': 'Grocery',
    'Fresh Vegetables': 'Grocery',
}

# 🔐 Use environment variables instead of hardcoding
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'your-default-bucket')
S3_FOLDER = os.environ.get('S3_FOLDER_PATH', 'csv-manual/')

s3_client = boto3.client('s3')


def generate_fake_data():
    num_records = random.randint(1, 5)
    data = []
    for _ in range(num_records):
        store_name = fake.company()
        store_address = fake.address()
        product_name, product_category = random.choice(list(PRODUCT_DICT.items()))
        product_price = round(fake.random.uniform(1.0, 100.0), 2)
        data.append({
            'StoreName': store_name,
            'StoreAddress': store_address,
            'ProductName': product_name,
            'ProductCategory': product_category,
            'ProductPrice': product_price
        })
    return data


def generate_csv(data):
    fieldnames = ['StoreName', 'StoreAddress', 'ProductName', 'ProductCategory', 'ProductPrice']
    csv_content = [','.join(fieldnames)]
    for record in data:
        row = [str(record[field]).replace('\n', ' ') for field in fieldnames]
        csv_content.append(','.join(row))
    return '\n'.join(csv_content)


def lambda_handler(event, context):
    try:
        fake_data = generate_fake_data()
        csv_content = generate_csv(fake_data)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        file_name = f'new_product_{timestamp}.csv'
        file_path = f'/tmp/{file_name}'

        with open(file_path, 'w') as csvfile:
            csvfile.write(csv_content)

        s3_key = f'{S3_FOLDER}{file_name}'
        s3_client.upload_file(file_path, S3_BUCKET, s3_key)

        print(f" CSV uploaded to S3: s3://{S3_BUCKET}/{s3_key}")

        return {
            'statusCode': 200,
            'body': f'CSV uploaded to S3 bucket at: s3://{S3_BUCKET}/{s3_key}'
        }

    except Exception as e:
        print(f" Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error occurred: {str(e)}'
        }
