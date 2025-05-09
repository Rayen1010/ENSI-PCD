import mysql.connector
from mysql.connector import Error
from datetime import datetime

def save_purchase_to_db(purchase_data):
    """Save customer purchase data to MySQL database using a single table"""
    host = "127.0.0.1"
    user = "root"
    password = "alphavision007" 
    database = "customerspurchases"
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create single table that matches report format (without frame_source)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS CustomerPurchases (
                customer_id INT AUTO_INCREMENT PRIMARY KEY,
                entry_datetime DATETIME NOT NULL,
                item_name VARCHAR(50) NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                item_total DECIMAL(10,2) NOT NULL,
                processing_date VARCHAR(20),
                total_amount DECIMAL(10,2) NOT NULL
            )
            """)
            connection.commit()
            
            # Insert data for each purchased item
            current_datetime = datetime.now()
            for item_name, item_data in purchase_data['customers'][0]['purchased_items'].items():
                cursor.execute("""
                INSERT INTO CustomerPurchases 
                (customer_id, entry_datetime, item_name, quantity, 
                 unit_price, item_total, processing_date, 
                 total_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    purchase_data['customers'][0]['customer_id'],
                    current_datetime,
                    item_name,
                    item_data['quantity'],
                    item_data['unit_price'],
                    item_data['item_total'],
                    purchase_data['metadata']['processing_date'],
                    purchase_data['customers'][0]['financial_summary']['total_amount']
                ))
            
            connection.commit()
            print(f"✔️ Saved purchase data for customer {purchase_data['customers'][0]['customer_id']}")

    except Error as e:
        print(f"❌ Database error: {e}")
        raise  # Re-raise the exception for the main script to handle
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
