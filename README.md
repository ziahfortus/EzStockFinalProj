# EzStockFinalProj
EzStock - Inventory Management System 

Project Overview
EzStock is an Inventory Management System built with Python and Tkinter. The system helps businesses manage their inventory efficiently by allowing the addition, updating, deletion, and sales tracking of products. It uses an SQLite database to store inventory and sales data. The system also includes a Sales History View and a user-friendly interface to monitor product availability and stock levels.

Features
User Authentication

Login system to access the inventory system.
CRUD Operations

Add, Update, and Delete products in the inventory.
Sales Functionality

Record sales transactions with automatic updates to the inventory.
Inventory Management

Monitor stock levels and get alerts for low stock items.
Sales History View

View detailed sales history with date, product name, quantity sold, and total sales.
User-Friendly Interface

Clean and intuitive UI built with Tkinter.
Technologies Used
Python 3.x
Tkinter for the GUI
SQLite for the database
datetime for timestamps

Prerequisites
Ensure you have Python installed on your system. You can check by running:
python --version
No need to install additional dependencies, as Tkinter and SQLite are built into Python.

Database Configuration
The system automatically creates an SQLite database named ezstock.db.
The database contains two main tables:
inventory - Stores product details (Item ID, Name, Quantity, Price, Category, Date Added).
sales_history - Keeps track of sales transactions (Date Sold, Product Name, Quantity Sold, Total Price).

How to Use
Login Page
Upon launching, you will be prompted to enter your login credentials (Username and Password).
Main Dashboard
The main window offers buttons to Add Items, Update Items, Delete Items, Sell Items, and View Sales History.
CRUD Operations
Use the provided form fields (Item ID, Item Name, Quantity, Price, Category) to:
Add: Insert new products into the system.
Update: Edit product details like name, quantity, and price.
Delete: Remove products from the inventory.
Sell: Record transactions and reduce stock quantity.
Sales History
Access the sales history to review transactions, clear history, and check product availability.

Troubleshooting
Database Connection Issues:
Ensure the sqlite3 module is properly installed. Python’s built-in sqlite3 should work by default.

GUI Errors:
If you experience GUI errors with Tkinter, ensure you have Tkinter installed. You can verify this with:
python -m tkinter

Empty Database Errors:
If tables do not appear in the database, make sure your script has run completely. Restart the application to recreate tables.

Suggest new features.
Report bugs with a detailed description.
Improve documentation and code readability.
