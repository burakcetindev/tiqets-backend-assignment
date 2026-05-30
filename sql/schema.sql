-- Data model for customers, orders, and barcodes.
-- Orders belong to customers, and barcodes optionally belong to orders.

CREATE TABLE customers (
    customer_id INT PRIMARY KEY
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE barcodes (
    barcode VARCHAR(32) PRIMARY KEY,
    order_id INT NULL,
    CONSTRAINT fk_barcodes_order
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_barcodes_order_id ON barcodes(order_id);
