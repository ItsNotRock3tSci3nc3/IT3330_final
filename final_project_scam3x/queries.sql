--PRODUCTS

--monthlyOrderTotals : Create and query a view that totals the dollar value for all the orders in the classic models database and groups the results by month and year. 
--The view should have the following columns: year, month, totalSales. 
CREATE OR REPLACE VIEW monthlyOrderTotals AS
SELECT YEAR(o.orderDate) AS year, MONTH(o.orderDate) AS month, SUM(od.quantityOrdered * od.priceEach) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY YEAR(o.orderDate), MONTH(o.orderDate);

-- Query the view
SELECT year, month, totalSales
FROM monthlyOrderTotals
ORDER BY year, month;

--orderLineTotals: Create and query a view that totals all the orders in the classic models database and groups the results by order line and year. 
--The view should have the following columns: year, productLine, totalSales.
CREATE OR REPLACE VIEW orderLineTotals AS
SELECT YEAR(o.orderDate) AS year, p.productLine AS productLine, SUM(od.quantityOrdered * od.priceEach) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p ON od.productCode = p.productCode
GROUP BY YEAR(o.orderDate), p.productLine;

-- Query the view
SELECT year, productLine, totalSales
FROM orderLineTotals
ORDER BY year, productLine;

--productOrderTotals: Create and query a view that totals all the orders in the classic models database and groups the results by product name and year. 
--The view should have the following columns: year, productName, totalSales.
CREATE OR REPLACE VIEW productOrderTotals AS
SELECT YEAR(o.orderDate) AS year, p.productName AS productName, SUM(od.quantityOrdered * od.priceEach) AS totalSales
FROM orders o
JOIN orderdetails od ON o.orderNumber = od.orderNumber
JOIN products p ON od.productCode = p.productCode
GROUP BY YEAR(o.orderDate), p.productName;

-- Query the view
SELECT year, productName, totalSales
FROM productOrderTotals
ORDER BY year, productName, totalSales DESC
LIMIT 10;

--CUSTOMERS

--customerOrderTotals: Create and query a view that totals the dollar value of all the customer orders in the classic models database and groups the results by customer and year. 
--The view should have the following columns: year, customerName, totalOrders. Results should show customers who have not made orders.
CREATE OR REPLACE VIEW customerOrderTotals AS
SELECT YEAR(o.orderDate) AS year, c.customerName, COALESCE(SUM(od.quantityOrdered * od.priceEach),0) AS totalOrders
FROM customers c
LEFT JOIN orders o ON c.customerNumber = o.customerNumber
LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
GROUP BY YEAR(o.orderDate), c.customerName;

-- Query the view
SELECT year, customerName, totalOrders
FROM customerOrderTotals
ORDER BY year, customerName;

--customerPaymentTotals: Create and query a view that totals all the payments by customer in the classic models database and groups the results by customer and year. 
--The view should have the following columns: year, customerName, totalPayments. Results should show customers who have not made payments.
CREATE OR REPLACE VIEW customerPaymentTotals AS
SELECT YEAR(p.paymentDate) AS year, c.customerName, COALESCE(SUM(p.amount), 0) AS totalPayments
FROM customers c
LEFT JOIN payments p ON c.customerNumber = p.customerNumber
GROUP BY YEAR(p.paymentDate), c.customerName;

-- Query the view
SELECT year, customerName, totalPayments
FROM customerPaymentTotals
ORDER BY customerName, year;