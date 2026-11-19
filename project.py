import csv  # Built-in module to read/write CSV files
import math  # Used to reject non-finite numbers such as nan or inf
import os  # Used to build file paths and check if files exist
from datetime import date, datetime  # date = today's date, datetime = validate YYYY-MM-DD text


# CONSTANTS: file names and column headers

BASE_DIR = os.path.dirname(os.path.abspath(__name__))  # Folder where this script lives, so CSVs are found from anywhere
MENU_FILE = os.path.join(BASE_DIR, "menu.csv")  # Full path of the menu CSV
TABLE_FILE = os.path.join(BASE_DIR, "tables.csv")  # Full path of the tables CSV
ORDER_FILE = os.path.join(BASE_DIR, "orders.csv")  # Full path of the order headers CSV
ITEM_FILE = os.path.join(BASE_DIR, "order_items.csv")  # Full path of the order lines CSV

MENU_FIELDS = ["item_id", "name", "category", "price", "available"]  # Menu columns
TABLE_FIELDS = ["table_id", "seats", "status"]  # Table columns
ORDER_FIELDS = ["order_id", "table_id", "order_date", "status"]  # Order header columns
ITEM_FIELDS = ["order_id", "item_id", "item_name", "quantity", "unit_price"]  # Order line columns (name and price are copied so old receipts never change)



# CSV HELPERS: create, load, save

def ensure_file(path, fields):  
    if not os.path.exists(path):  
        try:  
            with open(path, "w", newline="", encoding="utf-8") as f:  
                csv.DictWriter(f, fieldnames=fields).writeheader()  
        except OSError as err:  
            print(f"Could not create {path}: {err}")  


def load_csv(path, fields):  
    ensure_file(path, fields)  
    try:  
        with open(path, newline="", encoding="utf-8") as f:  
            return list(csv.DictReader(f))  
    except (OSError, csv.Error) as err:  
        print(f"Could not read {path}: {err}")  
        return []  

def save_csv(path, fields, rows):  
    try:  
        with open(path, "w", newline="", encoding="utf-8") as f: 
            writer = csv.DictWriter(f, fieldnames=fields)  
            writer.writeheader()  
            writer.writerows(rows)  
        return True  
    except OSError as err:  
        print(f"Could not save {path}: {err}")  
        return False  



# VALIDATION AND CALCULATION (pure functions, easy to unit test)

def parse_quantity(text):  
    try:  
        quantity = int(text)  
    except (ValueError, TypeError):  
        raise ValueError("Quantity must be a whole number.")  
    if quantity <= 0:  
        raise ValueError("Quantity must be greater than zero.")  
    return quantity 


def parse_price(text):  
    try:  
        price = float(text)  
    except (ValueError, TypeError):  
        raise ValueError("Price must be a number.")  
    if not math.isfinite(price) or price < 0:  
        raise ValueError("Price must be zero or more.")  
    return round(price, 2)  


def check_orderable(item):  
    if item is None:  
        raise ValueError("Menu item not found.")  
    if item["available"] != "Yes":  
        raise ValueError(f"'{item['name']}' is currently unavailable.")  


def line_total(unit_price, quantity):  
    return round(float(unit_price) * int(quantity), 2)  


def order_total(lines):  # Sum of all line totals in one order
    return round(sum(line_total(l["unit_price"], l["quantity"]) for l in lines), 2)  

def find_row(rows, key, value):  # Finds the first record whose column equals value (case-insensitive)
    for row in rows:  
        if row[key].lower() == value.strip().lower():  
            return row  
    return None   


def next_id(rows, key, prefix, width):  # Builds a new unique ID such as O031
    numbers = []  
    for row in rows:  
        suffix = row[key][len(prefix):]  
        if row[key].startswith(prefix) and suffix.isdigit():  
            numbers.append(int(suffix))  
    return f"{prefix}{max(numbers, default=0) + 1:0{width}d}"  

def build_line(menu, order_id, item_id, quantity_text):  # Validates input and returns a new order line
    item = find_row(menu, "item_id", item_id)  
    check_orderable(item)  
    quantity = parse_quantity(quantity_text)  
    return {  
        "order_id": order_id,  
        "item_id": item["item_id"],  
        "item_name": item["name"],  
        "quantity": quantity, 
        "unit_price": item["price"],  
    }  


def merge_line(lines, new_line):  # Adds a line, or increases quantity if the item is already in the order
    for line in lines:  
        if line["item_id"] == new_line["item_id"]:  
            line["quantity"] = int(line["quantity"]) + int(new_line["quantity"])  
            return  
    lines.append(new_line)  


def lines_for(order_id, items):  # All order lines belonging to one order
    return [i for i in items if i["order_id"] == order_id]  



# INPUT HELPERS AND PRINTING

def read_text(prompt):  # Asks until the user types something non-empty
    while True:  
        value = input(prompt).strip()  
        if value:  
            return value  
        print("Input cannot be empty.")  

def read_price(prompt):  # Asks until a valid price is typed
    while True:  
        try:  
            return parse_price(input(prompt))  
        except ValueError as err: 
            print(err)  


def confirm(prompt):  # Yes/No question; returns True for yes
    return input(prompt + " (y/n): ").strip().lower() == "y"  

def print_menu(rows):  # Shows menu records as a table
    if not rows:  
        print("No menu items found.")  
        return  # Stop
    print(f"{'ID':<7}{'Name':<28}{'Category':<10}{'Price':>8}  Available")  
    for r in rows:  # One line per item
        print(f"{r['item_id']:<7}{r['name']:<28}{r['category']:<10}{float(r['price']):>8.2f}  {r['available']}")  


def print_tables(rows):  # Shows table records
    if not rows:  
        print("No tables found.") 
        return  
    print(f"{'ID':<6}{'Seats':<7}Status")  
    for r in rows:  # One line per table
        print(f"{r['table_id']:<6}{r['seats']:<7}{r['status']}")  # Aligned values


def print_receipt(order, lines):  # Displays a simple receipt in the console
    print("\n" + "=" * 46)  
    print("            RESTAURANT RECEIPT")  
    print("=" * 46)  
    print(f"Order: {order['order_id']}   Table: {order['table_id']}")  
    print(f"Date:  {order['order_date']}   Status: {order['status']}")  
    print("-" * 46)  
    print(f"{'Item':<22}{'Qty':>4}{'Price':>9}{'Total':>10}")  
    for l in lines:  
        total = line_total(l["unit_price"], l["quantity"])  
        print(f"{l['item_name']:<22}{int(l['quantity']):>4}{float(l['unit_price']):>9.2f}{total:>10.2f}")  # Aligned row
    print("-" * 46)  # Divider
    print(f"{'TOTAL':<35}{order_total(lines):>11.2f}")  # Grand total
    print("=" * 46)  # Bottom border



# MENU MANAGEMENT

def add_menu_item():  # Adds a new menu record
    menu = load_csv(MENU_FILE, MENU_FIELDS)  # Load current menu
    name = read_text("Item name: ")  
    category = read_text("Category (Starter/Main/Side/Dessert/Drink): ")  
    price = read_price("Price: ")  
    new_item = {  
        "item_id": next_id(menu, "item_id", "M", 3),  
        "name": name,  
        "category": category,  
        "price": f"{price:.2f}",  
        "available": "Yes",  
    }  
    menu.append(new_item)  
    if save_csv(MENU_FILE, MENU_FIELDS, menu):  
        print(f"Added {new_item['name']} with ID {new_item['item_id']}.")  # Confirm


def search_menu():  # Searches by ID, name or category (partial match)
    menu = load_csv(MENU_FILE, MENU_FIELDS)  
    keyword = read_text("Search (ID, name or category): ").lower()  
    found = [m for m in menu if keyword in (m["item_id"] + " " + m["name"] + " " + m["category"]).lower()]  # Keep matches
    if found:  # At least one match
        print_menu(found)  # Show them
    else:  # No match
        print("No matching menu item.")  # Tell the user


def update_menu_item():  # Changes name, price or availability of an item
    menu = load_csv(MENU_FILE, MENU_FIELDS)  
    item = find_row(menu, "item_id", read_text("Item ID to update: "))  
    if item is None: 
        print("Menu item not found.") 
        return  
    print("Press Enter to keep the current value.")  
    new_name = input(f"Name [{item['name']}]: ").strip()  
    if new_name:  
        item["name"] = new_name  
    new_price = input(f"Price [{item['price']}]: ").strip()  
    if new_price: 
        try:  
            item["price"] = f"{parse_price(new_price):.2f}"  
        except ValueError as err:  # Invalid price
            print(f"{err} Update cancelled.") 
            return  # Stop without saving
    new_avail = input(f"Available Yes/No [{item['available']}]: ").strip().capitalize()  # Optional availability
    if new_avail in ("Yes", "No"):  # Valid choice
        item["available"] = new_avail  # Change the record
    elif new_avail:  # Typed something else
        print("Availability must be Yes or No. Update cancelled.")  # Explain
        return  # Stop without saving
    if save_csv(MENU_FILE, MENU_FIELDS, menu):  # Write to disk
        print("Menu item updated.")  # Confirm


def remove_menu_item():  # Deletes an item from the menu
    menu = load_csv(MENU_FILE, MENU_FIELDS)  # Load current menu
    item = find_row(menu, "item_id", read_text("Item ID to remove: "))  # Find the record
    if item is None:  # Not found
        print("Menu item not found.")  # Tell the user
        return  # Stop
    if confirm(f"Remove '{item['name']}'?"):  # Ask for confirmation
        menu.remove(item)  # Delete from the list
        if save_csv(MENU_FILE, MENU_FIELDS, menu):  # Write to disk
            print("Menu item removed.")  # Confirm
    else:  # User said no
        print("Nothing removed.")  # Tell the user


def manage_menu():  # Sub-menu for menu management
    while True:  # Repeat until Back
        print("\n--- Manage Menu Items ---") 
        print("1. Add  2. View all  3. Search  4. Update  5. Remove  6. Back")  
        choice = input("Choose: ").strip()  
        if choice == "1":  
            add_menu_item()  
        elif choice == "2":  
            print_menu(load_csv(MENU_FILE, MENU_FIELDS))  
        elif choice == "3":  
            search_menu()  
        elif choice == "4":  
            update_menu_item()  
        elif choice == "5":  
            remove_menu_item()  
        elif choice == "6":  
            return  
        else:  
            print("Invalid choice. Enter a number from 1 to 6.")  



# TABLE MANAGEMENT

def view_tables():  # Shows tables and lets staff change a status manually
    tables = load_csv(TABLE_FILE, TABLE_FIELDS)  # Load tables
    print_tables(tables)  
    if tables and confirm("Change a table's status?"):  # Optional manual change
        table = find_row(tables, "table_id", read_text("Table ID: "))  # Find the record
        if table is None: 
            print("Table not found.") 
            return  # Stop
        status = input("New status (Available/Occupied): ").strip().capitalize()  
        if status in ("Available", "Occupied"):  
            table["status"] = status  
            if save_csv(TABLE_FILE, TABLE_FIELDS, tables):  
                print("Table status updated.")  
        else:  
            print("Status must be Available or Occupied.")  


# ORDERS

def collect_lines(menu, order_id, lines):  # Loop asking for items until Enter is pressed
    while True:  # Repeat until user finishes
        item_id = input("Item ID (Enter to finish): ").strip()  # Read item ID
        if item_id == "":  # Empty means finished
            return  # Leave the loop
        quantity_text = input("Quantity: ").strip()  # Read quantity as text
        try:  # build_line may raise ValueError
            new_line = build_line(menu, order_id, item_id, quantity_text)  # Validate and build
        except ValueError as err:  # Unknown item, unavailable item or bad quantity
            print(f"Cannot add item: {err}")  # Explain
            continue  # Ask for the next item
        merge_line(lines, new_line)  # Add or merge into the order
        print(f"Added {new_line['quantity']} x {new_line['item_name']}.")  # Confirm


def create_order():  # Starts a new order for an available table
    tables = load_csv(TABLE_FILE, TABLE_FIELDS)  # Load tables
    menu = load_csv(MENU_FILE, MENU_FIELDS)  # Load menu
    orders = load_csv(ORDER_FILE, ORDER_FIELDS)  # Load order headers
    items = load_csv(ITEM_FILE, ITEM_FIELDS)  # Load order lines
    free = [t for t in tables if t["status"] == "Available"]  # Only available tables
    if not free:  # None free
        print("No tables are available.")  # Tell the user
        return  # Stop
    print_tables(free)  # Show free tables
    table = find_row(tables, "table_id", read_text("Table ID: "))  # Find chosen table
    if table is None:  # Not found
        print("Table not found.")  # Tell the user
        return  # Stop
    if table["status"] != "Available":  # Table already in use
        print("That table is occupied.")  # Tell the user
        return  # Stop
    print_menu([m for m in menu if m["available"] == "Yes"])  # Show only orderable items
    order_id = next_id(orders, "order_id", "O", 3)  # New unique order ID
    lines = []  # Order lines collected so far
    collect_lines(menu, order_id, lines)  # Ask for items
    if not lines:  # Nothing was ordered
        print("Empty order cancelled.")  # Do not save empty orders
        return  # Stop
    orders.append({"order_id": order_id, "table_id": table["table_id"], "order_date": date.today().isoformat(), "status": "Open"})  # New header, status Open
    items.extend(lines)  # Add the lines
    table["status"] = "Occupied"  # Table is now in use
    ok = save_csv(ORDER_FILE, ORDER_FIELDS, orders)  # Save headers
    ok = save_csv(ITEM_FILE, ITEM_FIELDS, items) and ok  # Save lines
    ok = save_csv(TABLE_FILE, TABLE_FIELDS, tables) and ok  # Save tables
    if ok:  # Everything saved
        print(f"Order {order_id} created. Total so far: {order_total(lines):.2f}")  # Confirm


def list_orders(orders, items):  # Prints a one-line summary per order
    print(f"{'Order':<7}{'Table':<7}{'Date':<12}{'Status':<11}{'Total':>9}")  # Column titles
    for o in orders:  # Each order
        total = order_total(lines_for(o["order_id"], items))  # Its total
        print(f"{o['order_id']:<7}{o['table_id']:<7}{o['order_date']:<12}{o['status']:<11}{total:>9.2f}")  # Aligned row


def view_update_order():  # View an order, add items, or complete it
    orders = load_csv(ORDER_FILE, ORDER_FIELDS)  # Load headers
    items = load_csv(ITEM_FILE, ITEM_FIELDS)  # Load lines
    if not orders:  # No data
        print("No orders recorded yet.")  # Tell the user
        return  # Stop
    list_orders(orders, items)  # Show all orders
    order = find_row(orders, "order_id", read_text("Order ID to open: "))  # Find the order
    if order is None:  # Not found
        print("Order not found.")  # Tell the user
        return  # Stop
    lines = lines_for(order["order_id"], items)  # Its lines
    print_receipt(order, lines)  # Show details
    if order["status"] == "Completed":  # Completed orders are read-only
        print("This order is completed and cannot be changed.")  # Explain
        return  # Stop
    print("1. Add items  2. Mark Completed  3. Back")  # Options for open orders
    choice = input("Choose: ").strip()  # Read choice
    if choice == "1":  # Add items
        menu = load_csv(MENU_FILE, MENU_FIELDS)  # Load menu
        collect_lines(menu, order["order_id"], lines)  # Ask for more items
        items = [i for i in items if i["order_id"] != order["order_id"]] + lines  # Replace old lines with updated ones
        if save_csv(ITEM_FILE, ITEM_FIELDS, items):  # Save
            print("Order updated.")  # Confirm
    elif choice == "2":  # Complete
        order["status"] = "Completed"  # Change status
        tables = load_csv(TABLE_FILE, TABLE_FIELDS)  # Load tables
        table = find_row(tables, "table_id", order["table_id"])  # Find its table
        if table is not None:  # Table exists
            table["status"] = "Available"  # Free the table
        ok = save_csv(ORDER_FILE, ORDER_FIELDS, orders)  # Save order
        ok = save_csv(TABLE_FILE, TABLE_FIELDS, tables) and ok  # Save table
        if ok:  # Saved
            print("Order marked Completed and table is now Available.")  # Confirm
    elif choice != "3":  # Not Back either
        print("Invalid choice.")  # Message


def bill_and_receipt():  # Shows the bill for any order
    orders = load_csv(ORDER_FILE, ORDER_FIELDS)  # Load headers
    items = load_csv(ITEM_FILE, ITEM_FIELDS)  # Load lines
    order = find_row(orders, "order_id", read_text("Order ID: "))  # Find the order
    if order is None:  # Not found
        print("Order not found.")  # Tell the user
        return  # Stop
    print_receipt(order, lines_for(order["order_id"], items))  # Display receipt



# REPORTS

def report_for_date(day, orders, items):  # Prints orders and sales for one date
    day_orders = [o for o in orders if o["order_date"] == day]  # Orders placed that day
    if not day_orders:  # None
        print(f"No orders recorded for {day}.")  # Tell the user
        return  # Stop
    list_orders(day_orders, items)  # Show them
    completed = [o for o in day_orders if o["status"] == "Completed"]  # Only completed count as sales
    sales = sum(order_total(lines_for(o["order_id"], items)) for o in completed)  # Add their totals
    print(f"Orders: {len(day_orders)}  Completed: {len(completed)}  Sales (completed): {sales:.2f}")  # Summary


def sales_report():  # Report sub-menu
    orders = load_csv(ORDER_FILE, ORDER_FIELDS)  # Load headers
    items = load_csv(ITEM_FILE, ITEM_FIELDS)  # Load lines
    print("1. Today's orders  2. Orders on a date  3. Total sales (all completed orders)  4. Back")  # Options
    choice = input("Choose: ").strip()  # Read choice
    if choice == "1":  # Today
        report_for_date(date.today().isoformat(), orders, items)  # Use today's date
    elif choice == "2":  # Specific date
        text = read_text("Date (YYYY-MM-DD): ")  # Read date text
        try:  # Validate the format
            datetime.strptime(text, "%Y-%m-%d")  # Raises ValueError if wrong
        except ValueError:  # Bad format
            print("Invalid date. Use YYYY-MM-DD.")  # Explain
            return  # Stop
        report_for_date(text, orders, items)  # Show that day
    elif choice == "3":  # All sales
        completed = [o for o in orders if o["status"] == "Completed"]  # Completed orders
        total = sum(order_total(lines_for(o["order_id"], items)) for o in completed)  # Add totals
        print(f"Completed orders: {len(completed)}  Total sales: {total:.2f}")  # Summary
    elif choice != "4":  # Not Back
        print("Invalid choice.")  # Message



# MAIN PROGRAM

def main():  # Program entry point
    for path, fields in ((MENU_FILE, MENU_FIELDS), (TABLE_FILE, TABLE_FIELDS), (ORDER_FILE, ORDER_FIELDS), (ITEM_FILE, ITEM_FIELDS)):  # All four files
        ensure_file(path, fields)  # Create any that are missing
    actions = {  # Maps menu numbers to functions
        "1": manage_menu,  # Menu management
        "2": view_tables,  # Tables
        "3": create_order,  # New order
        "4": view_update_order,  # View/update order
        "5": bill_and_receipt,  # Bill
        "6": sales_report,  # Reports
    }  # End of mapping
    while True:  # Main loop
        print("\n===== RESTAURANT MANAGEMENT SYSTEM =====")  # Title
        print("1. Manage Menu Items")  # Option 1
        print("2. View Tables")  # Option 2
        print("3. Create Order")  # Option 3
        print("4. View/Update Order")  # Option 4
        print("5. Calculate Bill / Print Receipt")  # Option 5
        print("6. Basic Sales Report")  # Option 6
        print("7. Exit")  # Option 7
        choice = input("Choose an option (1-7): ").strip()  # Read choice
        if choice == "7":  # Exit
            print("Goodbye!")  # Farewell
            break  # Leave the loop
        action = actions.get(choice)  # Look up the function
        if action:  # Valid number
            action()  # Run it
        else:  # Invalid
            print("Invalid choice. Enter a number from 1 to 7.")  # Message


if __name__ == "__main__":  # True only when run directly (not when imported by tests)
    try:  
        main()  # Start the program
    except (KeyboardInterrupt, EOFError):  # User interrupted input
        print("\nProgram closed.")  # Friendly exit