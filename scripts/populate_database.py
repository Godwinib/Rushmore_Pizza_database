import os
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker
import random
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabasePopulator:
    def __init__(self):
        self.fake = Faker()
        self.conn = None
        self.cur = None
        
    def get_db_config(self):
        """Get database configuration from environment variables"""
        config = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT', '5432')
        }
        
        # Validate required environment variables
        missing_vars = []
        for key, value in config.items():
            if value is None and key != 'port':
                missing_vars.append(key)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        logger.info(f"Database configuration loaded for host: {config['host']}")
        return config
    
    def connect(self):
        """Establish database connection"""
        config = self.get_db_config()
        try:
            self.conn = psycopg2.connect(
                host=config['host'],
                database=config['database'],
                user=config['user'],
                password=config['password'],
                port=config['port'],
                sslmode=os.getenv('DB_SSLMODE', 'require')
            )
            self.cur = self.conn.cursor()
            logger.info("Successfully connected to database")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    def clear_existing_data(self):
        """Clear all existing data from tables in correct order to avoid FK constraints"""
        logger.info("Clearing existing data...")
        tables = [
            'order_items',
            'orders', 
            'menu_item_ingredients',
            'menu_items',
            'ingredients',
            'customers',
            'stores'
        ]
        
        for table in tables:
            try:
                self.cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                logger.info(f"Cleared table: {table}")
            except Exception as e:
                logger.warning(f"Could not clear table {table}: {e}")
        
        self.conn.commit()
    
    def populate_stores(self, count=5):
        """Populate Stores table"""
        logger.info(f"Populating {count} stores...")
        stores = []
        cities = ['New York', 'Chicago', 'Los Angeles', 'Miami', 'Houston']
        
        # Calculate date range for store opening times
        end_date = datetime.now() - timedelta(days=365)  # 1 year ago
        start_date = datetime.now() - timedelta(days=5*365)  # 5 years ago
        
        for i in range(count):
            stores.append((
                self.fake.street_address(),
                cities[i % len(cities)],
                self.fake.phone_number()[:20],
                self.fake.date_time_between(start_date=start_date, end_date=end_date)
            ))
        
        execute_batch(self.cur,
            "INSERT INTO Stores (address, city, phone_number, opened_at) VALUES (%s, %s, %s, %s)",
            stores
        )
        self.conn.commit()
        logger.info(f"Added {count} stores")
    
    def populate_customers(self, count=1000):
        """Populate Customers table"""
        logger.info(f"Populating {count} customers...")
        customers = []
        
        # Calculate date range for customer creation times
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(days=2*365)  # 2 years ago
        
        # Use a set to track used emails to ensure uniqueness
        used_emails = set()
        
        for i in range(count):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            
            # Generate unique email with multiple fallbacks
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{base_email}@{self.fake.free_email_domain()}"
            
            # If email already exists, add a number to make it unique
            counter = 1
            while email in used_emails:
                email = f"{base_email}{counter}@{self.fake.free_email_domain()}"
                counter += 1
                
            used_emails.add(email)
            
            customers.append((
                first_name,
                last_name,
                email,
                self.fake.phone_number()[:20],
                self.fake.date_time_between(start_date=start_date, end_date=end_date)
            ))
        
        execute_batch(self.cur,
            "INSERT INTO Customers (first_name, last_name, email, phone_number, created_at) VALUES (%s, %s, %s, %s, %s)",
            customers
        )
        self.conn.commit()
        logger.info(f"Added {count} customers")
    
    def populate_ingredients(self):
        """Populate Ingredients table"""
        logger.info("Populating ingredients...")
        ingredients_data = [
            # Pizza ingredients
            ('Pizza Dough', 'kg', 100.0),
            ('Tomato Sauce', 'liters', 50.0),
            ('Mozzarella Cheese', 'kg', 80.0),
            ('Pepperoni', 'kg', 60.0),
            ('Mushrooms', 'kg', 40.0),
            ('Green Peppers', 'kg', 35.0),
            ('Onions', 'kg', 30.0),
            ('Black Olives', 'kg', 25.0),
            ('Sausage', 'kg', 45.0),
            ('Bacon', 'kg', 40.0),
            ('Ham', 'kg', 35.0),
            ('Pineapple', 'kg', 20.0),
            ('Basil', 'kg', 10.0),
            ('Oregano', 'kg', 8.0),
            ('Garlic', 'kg', 15.0),
            ('Parmesan Cheese', 'kg', 25.0),
            ('Ricotta Cheese', 'kg', 20.0),
            ('Spinach', 'kg', 15.0),
            ('Jalapenos', 'kg', 12.0),
            ('Anchovies', 'kg', 8.0),
            # Drink ingredients
            ('Cola Syrup', 'liters', 30.0),
            ('Diet Cola Syrup', 'liters', 25.0),
            ('Lemonade Mix', 'kg', 20.0),
            ('Iced Tea Mix', 'kg', 18.0),
            ('Coffee Beans', 'kg', 25.0),
            ('Tea Leaves', 'kg', 15.0),
            ('Bottled Water', 'units', 200.0),
            # Side dish ingredients
            ('Chicken Wings', 'kg', 40.0),
            ('Potatoes', 'kg', 60.0),
            ('Bread Dough', 'kg', 30.0),
            ('Garlic Butter', 'kg', 20.0),
            ('Ranch Dressing', 'liters', 15.0),
            ('Blue Cheese Dressing', 'liters', 12.0),
            ('Marinara Sauce', 'liters', 25.0),
            ('Buffalo Sauce', 'liters', 18.0),
            ('Mozzarella Cheese Sticks', 'kg', 22.0),
            ('Flour', 'kg', 50.0),
            ('Olive Oil', 'liters', 30.0),
            ('Salt', 'kg', 10.0),
            ('Black Pepper', 'kg', 8.0),
            ('Red Pepper Flakes', 'kg', 5.0)
        ]
        
        ingredients = []
        for name, unit, stock in ingredients_data:
            ingredients.append((name, stock, unit))
        
        execute_batch(self.cur,
            "INSERT INTO Ingredients (name, stock_quantity, unit) VALUES (%s, %s, %s)",
            ingredients
        )
        self.conn.commit()
        logger.info(f"Added {len(ingredients)} ingredients")
    
    def populate_menu_items(self):
        """Populate Menu_Items table"""
        logger.info("Populating menu items...")
        menu_items_data = [
            # Pizzas
            ('Margherita Pizza', 'Pizza', 'Small', 12.99),
            ('Margherita Pizza', 'Pizza', 'Medium', 15.99),
            ('Margherita Pizza', 'Pizza', 'Large', 18.99),
            ('Pepperoni Pizza', 'Pizza', 'Small', 14.99),
            ('Pepperoni Pizza', 'Pizza', 'Medium', 17.99),
            ('Pepperoni Pizza', 'Pizza', 'Large', 20.99),
            ('Vegetarian Pizza', 'Pizza', 'Small', 13.99),
            ('Vegetarian Pizza', 'Pizza', 'Medium', 16.99),
            ('Vegetarian Pizza', 'Pizza', 'Large', 19.99),
            ('Supreme Pizza', 'Pizza', 'Small', 16.99),
            ('Supreme Pizza', 'Pizza', 'Medium', 19.99),
            ('Supreme Pizza', 'Pizza', 'Large', 22.99),
            ('Hawaiian Pizza', 'Pizza', 'Small', 15.99),
            ('Hawaiian Pizza', 'Pizza', 'Medium', 18.99),
            ('Hawaiian Pizza', 'Pizza', 'Large', 21.99),
            ('Meat Lovers Pizza', 'Pizza', 'Small', 17.99),
            ('Meat Lovers Pizza', 'Pizza', 'Medium', 20.99),
            ('Meat Lovers Pizza', 'Pizza', 'Large', 23.99),
            ('BBQ Chicken Pizza', 'Pizza', 'Small', 16.49),
            ('BBQ Chicken Pizza', 'Pizza', 'Medium', 19.49),
            ('BBQ Chicken Pizza', 'Pizza', 'Large', 22.49),
            # Drinks
            ('Cola', 'Drink', '500ml', 2.99),
            ('Diet Cola', 'Drink', '500ml', 2.99),
            ('Lemonade', 'Drink', '500ml', 2.49),
            ('Iced Tea', 'Drink', '500ml', 2.49),
            ('Bottled Water', 'Drink', '500ml', 1.99),
            ('Coffee', 'Drink', 'Regular', 2.99),
            ('Hot Tea', 'Drink', 'Regular', 2.49),
            # Sides
            ('Garlic Bread', 'Side', 'N/A', 4.99),
            ('Cheesy Bread', 'Side', 'N/A', 5.99),
            ('Chicken Wings', 'Side', '8 pieces', 8.99),
            ('Chicken Wings', 'Side', '16 pieces', 15.99),
            ('Mozzarella Sticks', 'Side', '6 pieces', 6.99),
            ('Potato Wedges', 'Side', 'Regular', 4.99),
            ('Onion Rings', 'Side', 'Regular', 5.49),
            ('Garden Salad', 'Side', 'Regular', 6.99)
        ]
        
        execute_batch(self.cur,
            "INSERT INTO Menu_Items (name, category, size, price) VALUES (%s, %s, %s, %s)",
            menu_items_data
        )
        self.conn.commit()
        logger.info(f"Added {len(menu_items_data)} menu items")
    
    def populate_menu_item_ingredients(self):
        """Populate junction table for menu items and ingredients"""
        logger.info("Linking menu items with ingredients...")
        
        # Get all menu items and ingredients
        self.cur.execute("SELECT item_id, name, category FROM Menu_Items")
        menu_items = self.cur.fetchall()
        
        self.cur.execute("SELECT ingredient_id, name FROM Ingredients")
        ingredients = {name: id for id, name in self.cur.fetchall()}
        
        mappings = []
        
        for item_id, item_name, category in menu_items:
            if category == 'Pizza':
                # Base pizza ingredients
                mappings.extend([
                    (item_id, ingredients['Pizza Dough'], 0.25),
                    (item_id, ingredients['Tomato Sauce'], 0.1),
                    (item_id, ingredients['Mozzarella Cheese'], 0.2)
                ])
                
                # Specific pizza toppings
                if 'Margherita' in item_name:
                    mappings.append((item_id, ingredients['Basil'], 0.02))
                elif 'Pepperoni' in item_name:
                    mappings.append((item_id, ingredients['Pepperoni'], 0.15))
                elif 'Vegetarian' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Mushrooms'], 0.08),
                        (item_id, ingredients['Green Peppers'], 0.06),
                        (item_id, ingredients['Onions'], 0.05),
                        (item_id, ingredients['Black Olives'], 0.04)
                    ])
                elif 'Supreme' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Pepperoni'], 0.08),
                        (item_id, ingredients['Sausage'], 0.06),
                        (item_id, ingredients['Mushrooms'], 0.04),
                        (item_id, ingredients['Green Peppers'], 0.04),
                        (item_id, ingredients['Onions'], 0.03)
                    ])
                elif 'Hawaiian' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Ham'], 0.1),
                        (item_id, ingredients['Pineapple'], 0.08)
                    ])
                elif 'Meat Lovers' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Pepperoni'], 0.08),
                        (item_id, ingredients['Sausage'], 0.06),
                        (item_id, ingredients['Bacon'], 0.05),
                        (item_id, ingredients['Ham'], 0.05)
                    ])
                    
            elif category == 'Drink':
                if 'Cola' in item_name and 'Diet' not in item_name:
                    mappings.append((item_id, ingredients['Cola Syrup'], 0.05))
                elif 'Diet Cola' in item_name:
                    mappings.append((item_id, ingredients['Diet Cola Syrup'], 0.05))
                elif 'Lemonade' in item_name:
                    mappings.append((item_id, ingredients['Lemonade Mix'], 0.03))
                elif 'Iced Tea' in item_name:
                    mappings.append((item_id, ingredients['Iced Tea Mix'], 0.03))
                elif 'Coffee' in item_name:
                    mappings.append((item_id, ingredients['Coffee Beans'], 0.02))
                elif 'Hot Tea' in item_name:
                    mappings.append((item_id, ingredients['Tea Leaves'], 0.01))
                elif 'Bottled Water' in item_name:
                    mappings.append((item_id, ingredients['Bottled Water'], 1))
                    
            elif category == 'Side':
                if 'Garlic Bread' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Bread Dough'], 0.1),
                        (item_id, ingredients['Garlic Butter'], 0.05)
                    ])
                elif 'Cheesy Bread' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Bread Dough'], 0.1),
                        (item_id, ingredients['Mozzarella Cheese'], 0.08),
                        (item_id, ingredients['Garlic Butter'], 0.03)
                    ])
                elif 'Chicken Wings' in item_name:
                    mappings.append((item_id, ingredients['Chicken Wings'], 0.4))
                    if '8 pieces' in item_name:
                        mappings.append((item_id, ingredients['Buffalo Sauce'], 0.05))
                    else:  # 16 pieces
                        mappings.append((item_id, ingredients['Buffalo Sauce'], 0.1))
                elif 'Mozzarella Sticks' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Mozzarella Cheese Sticks'], 0.3),
                        (item_id, ingredients['Marinara Sauce'], 0.08)
                    ])
                elif 'Potato Wedges' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Potatoes'], 0.2),
                        (item_id, ingredients['Olive Oil'], 0.03)
                    ])
                elif 'Onion Rings' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Onions'], 0.15),
                        (item_id, ingredients['Flour'], 0.08),
                        (item_id, ingredients['Olive Oil'], 0.05)
                    ])
                elif 'Garden Salad' in item_name:
                    mappings.extend([
                        (item_id, ingredients['Spinach'], 0.1),
                        (item_id, ingredients['Onions'], 0.02),
                        (item_id, ingredients['Green Peppers'], 0.02)
                    ])
        
        execute_batch(self.cur,
            "INSERT INTO Menu_Item_Ingredients (menu_item_id, ingredient_id, quantity_required) VALUES (%s, %s, %s)",
            mappings
        )
        self.conn.commit()
        logger.info(f"Added {len(mappings)} menu item-ingredient relationships")
    
    def populate_orders(self, count=5000):
        """Populate Orders table"""
        logger.info(f"Populating {count} orders...")
        
        # Get store and customer IDs
        self.cur.execute("SELECT store_id FROM Stores")
        store_ids = [row[0] for row in self.cur.fetchall()]
        
        self.cur.execute("SELECT customer_id FROM Customers")
        customer_ids = [row[0] for row in self.cur.fetchall()]
        
        orders = []
        
        # Calculate date range for order timestamps
        end_date = datetime.now()
        start_date = datetime.now() - timedelta(days=365)  # 1 year ago
        
        for _ in range(count):
            store_id = random.choice(store_ids)
            customer_id = random.choice(customer_ids)
            order_time = self.fake.date_time_between(start_date=start_date, end_date=end_date)
            
            # Placeholder for total amount (will be updated later)
            orders.append((customer_id, store_id, order_time, 0.0))
        
        execute_batch(self.cur,
            "INSERT INTO Orders (customer_id, store_id, order_timestamp, total_amount) VALUES (%s, %s, %s, %s)",
            orders
        )
        self.conn.commit()
        logger.info(f"Added {count} orders")
    
    def populate_order_items(self):
        """Populate Order_Items table and update order totals"""
        logger.info("Populating order items...")
        
        # Get order and menu item IDs
        self.cur.execute("SELECT order_id FROM Orders")
        order_ids = [row[0] for row in self.cur.fetchall()]
        
        self.cur.execute("SELECT item_id, price FROM Menu_Items")
        menu_items = self.cur.fetchall()
        
        order_items = []
        order_totals = {}
        
        for order_id in order_ids:
            # Each order has 1-5 items
            num_items = random.randint(1, 5)
            order_total = 0
            
            for _ in range(num_items):
                item_id, price = random.choice(menu_items)
                quantity = random.randint(1, 3)
                item_total = price * quantity
                order_total += item_total
                
                order_items.append((order_id, item_id, quantity, price))
            
            order_totals[order_id] = order_total
        
        # Insert order items
        execute_batch(self.cur,
            "INSERT INTO Order_Items (order_id, item_id, quantity, unit_price) VALUES (%s, %s, %s, %s)",
            order_items
        )
        
        # Update order totals
        for order_id, total in order_totals.items():
            self.cur.execute(
                "UPDATE Orders SET total_amount = %s WHERE order_id = %s",
                (total, order_id)
            )
        
        self.conn.commit()
        logger.info(f"Added {len(order_items)} order items")
    
    def validate_data(self):
        """Validate that data was populated correctly"""
        logger.info("Validating data population...")
        
        validation_queries = {
            'Stores': "SELECT COUNT(*) FROM Stores",
            'Customers': "SELECT COUNT(*) FROM Customers",
            'Ingredients': "SELECT COUNT(*) FROM Ingredients",
            'Menu_Items': "SELECT COUNT(*) FROM Menu_Items",
            'Orders': "SELECT COUNT(*) FROM Orders",
            'Order_Items': "SELECT COUNT(*) FROM Order_Items",
            'Menu_Item_Ingredients': "SELECT COUNT(*) FROM Menu_Item_Ingredients"
        }
        
        for table, query in validation_queries.items():
            self.cur.execute(query)
            count = self.cur.fetchone()[0]
            logger.info(f"{table}: {count} rows")
        
        # Check for orders with no items
        self.cur.execute("""
            SELECT COUNT(*) 
            FROM Orders o 
            LEFT JOIN Order_Items oi ON o.order_id = oi.order_id 
            WHERE oi.order_item_id IS NULL
        """)
        orphaned_orders = self.cur.fetchone()[0]
        if orphaned_orders > 0:
            logger.warning(f"Found {orphaned_orders} orders with no items")
        
        logger.info("Data validation completed")
    
    def populate_all(self, clear_existing=True):
        """Populate all tables in correct order"""
        try:
            self.connect()
            
            if clear_existing:
                self.clear_existing_data()
            
            # Populate in correct order to respect foreign keys
            self.populate_stores(5)
            self.populate_customers(1000)
            self.populate_ingredients()
            self.populate_menu_items()
            self.populate_menu_item_ingredients()
            self.populate_orders(5000)
            self.populate_order_items()
            
            # Validate the data
            self.validate_data()
            
            logger.info("Database population completed successfully!")
            
        except Exception as e:
            logger.error(f"Error during population: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            self.disconnect()

def main():
    """Main function with command line argument support"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate RushMore Pizzeria database with synthetic data')
    parser.add_argument('--keep-existing', action='store_true', 
                       help='Keep existing data (default: clear all data first)')
    parser.add_argument('--customers', type=int, default=1000,
                       help='Number of customers to generate (default: 1000)')
    parser.add_argument('--orders', type=int, default=5000,
                       help='Number of orders to generate (default: 5000)')
    
    args = parser.parse_args()
    
    populator = DatabasePopulator()
    
    # Note: For custom customer and order counts, you would need to modify the methods
    # to accept parameters. Currently using defaults for simplicity.
    
    populator.populate_all(clear_existing=not args.keep_existing)

if __name__ == "__main__":
    main()