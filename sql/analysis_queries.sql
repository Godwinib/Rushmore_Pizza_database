-- 1. Total sales revenue per store
SELECT 
    s.store_id,
    s.city,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    ROUND(AVG(o.total_amount), 2) as avg_order_value
FROM Stores s
JOIN Orders o ON s.store_id = o.store_id
GROUP BY s.store_id, s.city
ORDER BY total_revenue DESC;

-- 2. Top 10 most valuable customers
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent,
    ROUND(AVG(o.total_amount), 2) as avg_order_value
FROM Customers c
JOIN Orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC
LIMIT 10;

-- 3. Most popular menu items by quantity sold
SELECT 
    mi.name,
    mi.category,
    mi.size,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.quantity * oi.unit_price) as total_revenue
FROM Menu_Items mi
JOIN Order_Items oi ON mi.item_id = oi.item_id
GROUP BY mi.item_id, mi.name, mi.category, mi.size
ORDER BY total_quantity_sold DESC
LIMIT 15;

-- 4. Average order value
SELECT 
    ROUND(AVG(total_amount), 2) as overall_avg_order_value,
    MIN(total_amount) as min_order_value,
    MAX(total_amount) as max_order_value
FROM Orders;

-- 5. Busiest hours of the day for orders
SELECT 
    EXTRACT(HOUR FROM order_timestamp) as hour_of_day,
    COUNT(*) as order_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Orders), 2) as percentage
FROM Orders
GROUP BY hour_of_day
ORDER BY order_count DESC;

-- Additional useful queries:

-- Monthly revenue trend
SELECT 
    DATE_TRUNC('month', order_timestamp) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue
FROM Orders
GROUP BY month
ORDER BY month;

-- Customer retention analysis
SELECT 
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) as returning_customers,
    ROUND(COUNT(DISTINCT CASE WHEN order_count > 1 THEN customer_id END) * 100.0 / COUNT(DISTINCT customer_id), 2) as retention_rate
FROM (
    SELECT customer_id, COUNT(*) as order_count
    FROM Orders
    GROUP BY customer_id
) customer_orders;