import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
import sqlite3  # SQLite import

# Connect to SQLite database (or create it)
conn = sqlite3.connect("ezstock.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    category TEXT NOT NULL,
    date_added TEXT NOT NULL
)
""")
conn.commit()

# Sales history and totals (optional, can be used for sales tracking)
sales_history = []
total_sales = 0
total_expenses = 0
low_stock_alerted = set()  # Track items that already triggered the low stock alert

# Function to verify login credentials
def verify_login():
    username = username_entry.get()
    password = password_entry.get()
    if username and password:  # You can change this check to a more robust verification system
        # Show welcome pop-up first
        messagebox.showinfo("Welcome", f"Welcome, {username}!")
        login_window.destroy()  # Close the login window
        main_window(username)  # Open the main window
    else:
        messagebox.showerror("Login Failed", "Please enter both username and password.")

# Main application window
def main_window(username):
    root = tk.Tk()
    root.title("EzStock - Inventory Management")
    root.geometry("800x600")
    root.configure(bg="#f8d9e4")

    # Define functions for actions inside the main window
    def add_item():
        if not validate_fields():
            return
        item_id = entry_id.get()
        name = entry_name.get().title()
        quantity = entry_quantity.get()
        price = entry_price.get()
        category = category_combobox.get()

        if item_id.isdigit() and name and quantity and price and category:
            date_added = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                # Validate price and quantity
                price = float(price.replace('₱', '').replace(',', '').strip())
                quantity = int(quantity)

                if quantity <= 0:  # Check for valid quantity
                    raise ValueError("Quantity must be a positive number.")

                # Insert the item into the database
                cursor.execute("""
                INSERT INTO inventory (id, name, quantity, price, category, date_added)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (item_id, name, quantity, price, category, date_added))
                conn.commit()
                messagebox.showinfo("Success", f"Item '{name}' added to inventory.")
                refresh_inventory_list()
                clear_entries()
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Error: {str(e)}. Please enter a valid price and quantity.")
        else:
            messagebox.showerror("Input Error", "Please fill in all fields with valid data.")

    def update_item():
        if not validate_fields():
            return
        item_id = entry_id.get()
        if not item_id.isdigit():  # Check if Item ID is numeric
            messagebox.showerror("Invalid Item ID", "Item ID must be numeric.")
            return

        name = entry_name.get()
        quantity = entry_quantity.get()
        price = entry_price.get()
        category = category_combobox.get()

        try:
            price = float(price.replace('₱', '').replace(',', '').strip())
            quantity = int(quantity)
            cursor.execute("""
            UPDATE inventory
            SET name = ?, quantity = ?, price = ?, category = ?
            WHERE id = ?
            """, (name, quantity, price, category, item_id))
            conn.commit()
            messagebox.showinfo("Success", f"Item '{name}' updated.")
            refresh_inventory_list()
            clear_entries()
        except sqlite3.Error:
            messagebox.showerror("Not Found", "Item ID not found in inventory.")
            
    def delete_item():
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete.")
            return

        item_details = tree.item(selected_item, "values")
        item_id = item_details[0]
        item_name = item_details[1] 

        confirm = messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete '{item_name}' (ID: {item_id})?")
        if confirm:
            try:
                cursor.execute("DELETE FROM Inventory WHERE id = ?" , (item_id,))
                conn.commit()
                messagebox.showinfo("Deleted", f"item '{item_name}' (ID: {item_id}) deleted successfully.")
                refresh_inventory_list()
            except Exception as e:
                messagebox.showerror("Error" f"Failed to delete item: {e}")

    def sell_item():
        item_id_or_name = entry_id.get()  # Item ID o Product Name
        quantity_to_sell = entry_quantity.get()

        if not item_id_or_name or not quantity_to_sell.isdigit() or int(quantity_to_sell) <= 0:
            messagebox.showerror("Invalid Input", "Please provide a valid Item ID/Name and a positive quantity to sell.")
            return

        quantity_to_sell = int(quantity_to_sell)

        try:
            # Query the database to find the item
            cursor.execute("SELECT * FROM inventory WHERE id = ? OR name = ?", (item_id_or_name, item_id_or_name))
            item = cursor.fetchone()

            if item:
                current_quantity = item[2]  # Current quantity in stock
                item_id = item[0]
                item_name = item[1]
                item_price = item[3]

                if current_quantity >= quantity_to_sell:
                    #Deduct quantity from inventory
                    new_quantity = current_quantity - quantity_to_sell

                    cursor.execute("""
                        UPDATE inventory
                        SET quantity = ?
                        WHERE id = ?
                    """, (new_quantity, item_id))
                    conn.commit()

                    # Record sale in sales_history table
                    sales_price = item_price * quantity_to_sell  # Total sales price

                    cursor.execute("""
                        INSERT INTO sales_history (product_name, quantity_sold, total_price, date_sold)
                        VALUES (?, ?, ?, ?)
                    """, (item_name, quantity_to_sell, sales_price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()

                    messagebox.showinfo("Sold", f"Successfully sold {quantity_to_sell} units of '{item_name}'.")
                    if new_quantity <= 10:
                        messagebox.showwarning("Low Stock Alert", f"Item '{item_name}' has low stock (only {new_quantity} left).")
                        
                    # Refresh the inventory list
                    refresh_inventory_list()
                    clear_entries()

                else:
                    messagebox.showerror("Error", f"Not enough stock to sell. Available quantity: {current_quantity}")

            else:
                messagebox.showerror("Not Found", "Item not found in inventory. Please check the Item ID or Name.")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to sell item: {str(e)}")


        # Function to view sales history
    def view_sales_history():
        history_window = tk.Toplevel(root)
        history_window.title("Sales History")
        history_window.geometry("600x400")
        history_window.configure(bg="#f8d9e4")

        tk.Label(history_window, text="Sales History", font=("Segoe UI", 16, "bold"), bg="#f8d9e4").pack(pady=10)

        tree_history = ttk.Treeview(history_window, 
                                    columns=("Date Sold", "Product Name", "Quantity Sold", "Total Price"), 
                                    show="headings", 
                                    height=15)

        tree_history.pack(fill=tk.BOTH, expand=True)

        # Define headings for treeview
        for col in tree_history["columns"]:
            tree_history.heading(col, text=col, anchor=tk.CENTER)
            tree_history.column(col, anchor=tk.CENTER, width=150)

        # Fetch sales data from database
        cursor.execute("SELECT date_sold, product_name, quantity_sold, total_price FROM sales_history ORDER BY date_sold DESC")
        rows = cursor.fetchall()

        if rows:
            for row in rows:
                tree_history.insert("", tk.END, values=row)
        else:
            messagebox.showinfo("No Data", "No sales history available.")
    
        def clear_sales_history():
            confirm_clear = messagebox.askyesno("Clear History", "Are you sure you want to clear all sales history?")
            if confirm_clear:
                try:
                    cursor.execute("DELETE FROM sales_history")
                    conn.commit()
                    messagebox.showinfo("History Cleared", "All sales history has been cleared.")
                    tree_history.delete(*tree_history.get_children())
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to clear history: {e}")

        clear_button = tk.Button(history_window, text="Clear Sales History", font=("Segoe UI", 12, "bold"), bg="red", fg="white", command=clear_sales_history)
        clear_button.pack(pady=10)


    def refresh_inventory_list():
        # Clear the treeview
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute("SELECT * FROM inventory")
        for row in cursor.fetchall():
            item_id, name, quantity, price, category, date_added = row
            color = "white"
            if quantity <= 10:  # Low stock alert (this will not trigger the popup alert again)
                color = "red"
            tree.insert("", "end", values=(
                item_id,
                name,
                quantity,
                f"₱{price:,.2f}",
                category,
                date_added
            ), tags=(color,))
        tree.tag_configure("red", background="red", foreground="white")  # Highlight low stock in red

    def clear_entries():
        entry_id.delete(0, tk.END)
        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        category_combobox.set('')

    def validate_fields():
        if not entry_id.get() or not entry_name.get() or not entry_quantity.get() or not entry_price.get() or not category_combobox.get():
            messagebox.showerror("Input Error", "Please fill in all fields with valid data.")
            return False
        return True

    # Input fields frame
    frame = tk.Frame(root, bg="#f8d9e4")
    frame.pack(pady=20)

    tk.Label(frame, text="Item ID", bg="#f8d9e4", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    entry_id = tk.Entry(frame, width=30, font=("Segoe UI", 12), relief="solid", bd=2)
    entry_id.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(frame, text="Item Name", bg="#f8d9e4", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    entry_name = tk.Entry(frame, width=30, font=("Segoe UI", 12), relief="solid", bd=2)
    entry_name.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(frame, text="Quantity", bg="#f8d9e4", font=("Segoe UI", 12, "bold")).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    entry_quantity = tk.Entry(frame, width=30, font=("Segoe UI", 12), relief="solid", bd=2)
    entry_quantity.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(frame, text="Price (₱)", bg="#f8d9e4", font=("Segoe UI", 12, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
    entry_price = tk.Entry(frame, width=30, font=("Segoe UI", 12), relief="solid", bd=2)
    entry_price.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(frame, text="Category", bg="#f8d9e4", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, padx=10, pady=10, sticky="e")
    category_combobox = ttk.Combobox(frame, values=["Food", "Beauty Products", "Toys", "Medicine", "Clothing", "Stationery", "Home & Living", "Electronics & Gadgets"], font=("Segoe UI", 12), width=28, state="readonly")
    category_combobox.grid(row=4, column=1, padx=10, pady=10)

    # Buttons frame
    button_frame = tk.Frame(root, bg="#f8d9e4")
    button_frame.pack(pady=20)

    button_style = {'font': ("Segoe UI", 12, "bold"), 'bg': "#F62681", 'fg': "white", 'width': 15, 'height': 2}

    add_button = tk.Button(button_frame, text="Add Item", command=add_item, **button_style)
    add_button.grid(row=0, column=0, padx=10, pady=10)

    update_button = tk.Button(button_frame, text="Update Item", command=update_item, **button_style)
    update_button.grid(row=0, column=1, padx=10, pady=10)

    delete_button = tk.Button(button_frame, text="Delete Item", command=delete_item, **button_style)
    delete_button.grid(row=0, column=2, padx=10, pady=10)

    sell_button = tk.Button(button_frame, text="Sell Item", command=sell_item, **button_style)
    sell_button.grid(row=0, column=3, padx=10, pady=10)

    history_button = tk.Button(button_frame, text="View Sales History", command=view_sales_history, **button_style)
    history_button.grid(row=0, column=4, padx=10, pady=10)

    # Inventory List (Treeview)
    tree_frame = tk.Frame(root, bg="#f8d9e4")
    tree_frame.pack(pady=20)

    tree = ttk.Treeview(tree_frame, 
                        columns=("ID", "Name", "Quantity", "Price", "Category", "Date Added"), 
                        show="headings", 
                        height=10)
    tree.grid(row=0, column=0, sticky="nsew")

    for col in tree["columns"]:
        tree.heading(col, text=col, anchor=tk.CENTER)
        tree.column(col, anchor=tk.CENTER, width=120)

    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    tree.configure(yscrollcommand=scrollbar.set)

    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    refresh_inventory_list()

    root.mainloop()

# Login window
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x250")
login_window.configure(bg="#f8d9e4")

# Add a welcome message before login form
welcome_label = tk.Label(login_window, text="Welcome to EzStock!", font=("Segoe UI", 16, "bold"), fg="#F62681", bg="#f8d9e4")
welcome_label.pack(pady=20)

# Username and Password Entry
tk.Label(login_window, text="Username", font=("Segoe UI", 12, "bold"), bg="#f8d9e4").pack(pady=5)
username_entry = tk.Entry(login_window, font=("Segoe UI", 12))
username_entry.pack(pady=5)

tk.Label(login_window, text="Password", font=("Segoe UI", 12, "bold"), bg="#f8d9e4").pack(pady=5)
password_entry = tk.Entry(login_window, font=("Segoe UI", 12), show="*")
password_entry.pack(pady=5)

login_button = tk.Button(login_window, text="Login", font=("Segoe UI", 12, "bold"), bg="#F62681", fg="white", command=verify_login)
login_button.pack(pady=20)

login_window.mainloop()
