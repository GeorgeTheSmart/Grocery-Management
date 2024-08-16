import tkinter as tk
from tkinter import messagebox
import sqlite3

class GroceryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grocery Inventory Management")
        self.root.configure(bg='#023e8a')
        self.root.geometry('1920x1080')  # Full-screen window size

        # Center the main content
        self.frame = tk.Frame(root, bg='#023e8a')
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        # Setup Database
        self.setup_database()

        # Main Inventory Section
        tk.Label(self.frame, text="Main Inventory", bg='#023e8a', fg='white', font=('Arial', 24, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        tk.Label(self.frame, text="Item Name:", bg='#023e8a', fg='white', font=('Arial', 18)).grid(row=1, column=0, padx=20, pady=10)
        self.item_name_entry = tk.Entry(self.frame, font=('Arial', 18))
        self.item_name_entry.grid(row=1, column=1, padx=20, pady=10)
        tk.Label(self.frame, text="Quantity:", bg='#023e8a', fg='white', font=('Arial', 18)).grid(row=2, column=0, padx=20, pady=10)
        self.quantity_entry = tk.Entry(self.frame, font=('Arial', 18))
        self.quantity_entry.grid(row=2, column=1, padx=20, pady=10)
        tk.Button(self.frame, text="Add Item", command=self.add_item, bg='#ff006e', fg='white', font=('Arial', 18)).grid(row=3, column=0, columnspan=2, pady=20)

        # Transfer Section
        tk.Label(self.frame, text="Transfer to Checkout", bg='#023e8a', fg='white', font=('Arial', 24, 'bold')).grid(row=4, column=0, columnspan=2, pady=20)
        tk.Label(self.frame, text="Item Name:", bg='#023e8a', fg='white', font=('Arial', 18)).grid(row=5, column=0, padx=20, pady=10)
        self.transfer_item_name_entry = tk.Entry(self.frame, font=('Arial', 18))
        self.transfer_item_name_entry.grid(row=5, column=1, padx=20, pady=10)
        tk.Label(self.frame, text="Quantity:", bg='#023e8a', fg='white', font=('Arial', 18)).grid(row=6, column=0, padx=20, pady=10)
        self.transfer_quantity_entry = tk.Entry(self.frame, font=('Arial', 18))
        self.transfer_quantity_entry.grid(row=6, column=1, padx=20, pady=10)
        tk.Button(self.frame, text="Transfer Item", command=self.transfer_item, bg='#ff006e', fg='white', font=('Arial', 18)).grid(row=7, column=0, columnspan=2, pady=20)

        # Delete Section
        tk.Label(self.frame, text="Delete Item", bg='#023e8a', fg='white', font=('Arial', 24, 'bold')).grid(row=8, column=0, columnspan=2, pady=20)
        tk.Label(self.frame, text="Item Name:", bg='#023e8a', fg='white', font=('Arial', 18)).grid(row=9, column=0, padx=20, pady=10)
        self.delete_item_name_entry = tk.Entry(self.frame, font=('Arial', 18))
        self.delete_item_name_entry.grid(row=9, column=1, padx=20, pady=10)
        tk.Button(self.frame, text="Delete Item", command=self.delete_item, bg='#ff006e', fg='white', font=('Arial', 18)).grid(row=10, column=0, columnspan=2, pady=20)

        # Inventory List
        tk.Label(self.frame, text="Current Inventory", bg='#023e8a', fg='white', font=('Arial', 24, 'bold')).grid(row=11, column=0, columnspan=2, pady=20)
        self.inventory_listbox = tk.Listbox(self.frame, width=80, height=15, bg='#f0f0f0', font=('Arial', 18))
        self.inventory_listbox.grid(row=12, column=0, columnspan=2, padx=20, pady=20)
        self.update_inventory_list()

    def setup_database(self):
        conn = sqlite3.connect('grocery_inventory.db')
        c = conn.cursor()
        # Create inventory table
        c.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL
            )
        ''')
        # Create checkout_inventory table
        c.execute('''
            CREATE TABLE IF NOT EXISTS checkout_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def execute_db_query(self, query, parameters=()):
        conn = sqlite3.connect('grocery_inventory.db')
        c = conn.cursor()
        c.execute(query, parameters)
        conn.commit()
        conn.close()

    def fetch_data(self, query, parameters=()):
        conn = sqlite3.connect('grocery_inventory.db')
        c = conn.cursor()
        c.execute(query, parameters)
        data = c.fetchall()
        conn.close()
        return data

    def add_item(self):
        item_name = self.item_name_entry.get()
        quantity = self.quantity_entry.get()
        if item_name and quantity.isdigit():
            self.execute_db_query('''
                INSERT INTO inventory (item_name, quantity)
                VALUES (?, ?)
                ON CONFLICT(item_name) DO UPDATE SET quantity = quantity + excluded.quantity
            ''', (item_name, int(quantity)))
            self.update_inventory_list()
            self.item_name_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a valid item name and quantity.")

    def transfer_item(self):
        item_name = self.transfer_item_name_entry.get()
        quantity = self.transfer_quantity_entry.get()
        if item_name and quantity.isdigit():
            item = self.fetch_data('SELECT * FROM inventory WHERE item_name = ?', (item_name,))
            if item and item[0][2] >= int(quantity):
                self.execute_db_query('''
                    INSERT INTO checkout_inventory (item_name, quantity)
                    VALUES (?, ?)
                    ON CONFLICT(item_name) DO UPDATE SET quantity = quantity + excluded.quantity
                ''', (item_name, int(quantity)))
                self.execute_db_query('UPDATE inventory SET quantity = quantity - ? WHERE item_name = ?', (int(quantity), item_name))
                self.update_inventory_list()
                self.transfer_item_name_entry.delete(0, tk.END)
                self.transfer_quantity_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Transfer Error", "Not enough stock or item does not exist.")
        else:
            messagebox.showwarning("Input Error", "Please enter a valid item name and quantity.")

    def delete_item(self):
        item_name = self.delete_item_name_entry.get()
        if item_name:
            self.execute_db_query('DELETE FROM inventory WHERE item_name = ?', (item_name,))
            self.update_inventory_list()
            self.delete_item_name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter an item name.")

    def update_inventory_list(self):
        self.inventory_listbox.delete(0, tk.END)
        items = self.fetch_data('SELECT item_name, quantity FROM inventory')
        for item in items:
            self.inventory_listbox.insert(tk.END, f"{item[0]}: {item[1]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryApp(root)
    root.mainloop()
