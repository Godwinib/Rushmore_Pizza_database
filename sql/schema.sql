-- RushMore Pizzeria Database Schema
-- Created for Capstone Project

-- Stores table
CREATE TABLE Stores (
    store_id SERIAL PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ingredients table
CREATE TABLE Ingredients (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    stock_quantity NUMERIC(10, 2) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL
);

-- Menu_Items table
CREATE TABLE Menu_Items (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    size VARCHAR(20),
    price NUMERIC(10, 2) NOT NULL
);

-- Menu_Item_Ingredients junction table (for many-to-many relationship)
CREATE TABLE Menu_Item_Ingredients (
    menu_item_id INTEGER REFERENCES Menu_Items(item_id),
    ingredient_id INTEGER REFERENCES Ingredients(ingredient_id),
    quantity_required NUMERIC(8, 2) NOT NULL,
    PRIMARY KEY (menu_item_id, ingredient_id)
);

-- Orders table
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES Customers(customer_id) ON DELETE SET NULL,
    store_id INTEGER REFERENCES Stores(store_id) ON DELETE RESTRICT,
    order_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'completed'
);

-- Order_Items table
CREATE TABLE Order_Items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES Orders(order_id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES Menu_Items(item_id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price NUMERIC(10, 2) NOT NULL
);

-- Indexes for performance
CREATE INDEX idx_orders_customer_id ON Orders(customer_id);
CREATE INDEX idx_orders_store_id ON Orders(store_id);
CREATE INDEX idx_orders_timestamp ON Orders(order_timestamp);
CREATE INDEX idx_order_items_order_id ON Order_Items(order_id);
CREATE INDEX idx_customers_email ON Customers(email);