from datetime import date, timedelta
import project as app  # Replace 'restaurant' with your main script's filename (without .py)


def seed_thirty_five_each(count=35):
    # Keep CSV paths anchored to the script's directory if imported
    if hasattr(app, "__file__"):
        app.BASE_DIR = app.os.path.dirname(app.os.path.abspath(app.__file__))
        app.MENU_FILE = app.os.path.join(app.BASE_DIR, "menu.csv")
        app.TABLE_FILE = app.os.path.join(app.BASE_DIR, "tables.csv")
        app.ORDER_FILE = app.os.path.join(app.BASE_DIR, "orders.csv")
        app.ITEM_FILE = app.os.path.join(app.BASE_DIR, "order_items.csv")

    for path, fields in (
        (app.MENU_FILE, app.MENU_FIELDS),
        (app.TABLE_FILE, app.TABLE_FIELDS),
        (app.ORDER_FILE, app.ORDER_FIELDS),
        (app.ITEM_FILE, app.ITEM_FIELDS),
    ):
        app.ensure_file(path, fields)

    menu = app.load_csv(app.MENU_FILE, app.MENU_FIELDS)
    tables = app.load_csv(app.TABLE_FILE, app.TABLE_FIELDS)
    orders = app.load_csv(app.ORDER_FILE, app.ORDER_FIELDS)
    items = app.load_csv(app.ITEM_FILE, app.ITEM_FIELDS)

    base_dishes = [
        ("Garlic Bread", "Starter", 4.50),
        ("Caesar Salad", "Starter", 7.00),
        ("Tomato Soup", "Starter", 5.50),
        ("Bruschetta", "Starter", 6.00),
        ("Spring Rolls", "Starter", 5.00),
        ("Margherita Pizza", "Main", 12.50),
        ("Grilled Chicken", "Main", 15.00),
        ("Beef Burger", "Main", 13.50),
        ("Pasta Alfredo", "Main", 14.00),
        ("Fish and Chips", "Main", 14.50),
        ("French Fries", "Side", 4.00),
        ("Steamed Rice", "Side", 3.50),
        ("Mashed Potatoes", "Side", 4.25),
        ("Tiramisu", "Dessert", 6.50),
        ("Cheesecake", "Dessert", 6.75),
        ("Lemonade", "Drink", 3.50),
        ("Iced Tea", "Drink", 3.25),
        ("Espresso", "Drink", 3.00),
    ]

    # 1. Add 35 menu items
    added_menu = []
    for i in range(count):
        dish_name, category, base_price = base_dishes[i % len(base_dishes)]
        variant = f" #{(i // len(base_dishes)) + 1}" if i >= len(base_dishes) else ""
        price = round(base_price + (i % 4) * 0.50, 2)
        avail = "No" if i % 9 == 8 else "Yes"
        row = {
            "item_id": app.next_id(menu, "item_id", "M", 3),
            "name": f"{dish_name}{variant}",
            "category": category,
            "price": f"{app.parse_price(price):.2f}",
            "available": avail,
        }
        menu.append(row)
        added_menu.append(row)

    # 2. Add 35 tables
    seat_pattern = [2, 2, 4, 4, 6, 8]
    added_tables = []
    for i in range(count):
        row = {
            "table_id": app.next_id(tables, "table_id", "T", 2),
            "seats": str(seat_pattern[i % len(seat_pattern)]),
            "status": "Available",
        }
        tables.append(row)
        added_tables.append(row)

    # 3. Add 35 orders and 35 order_items (1 line item per order)
    orderable_ids = [m["item_id"] for m in added_menu if m["available"] == "Yes"]
    today = date.today()
    added_orders = []
    added_items = []

    for i in range(count):
        order_id = app.next_id(orders, "order_id", "O", 3)
        table_row = added_tables[i]
        day_offset = i % 5
        order_date = (today - timedelta(days=day_offset)).isoformat()
        is_open = i >= (count - 5)  # Last 5 orders Open (and occupy their tables)
        status = "Open" if is_open else "Completed"

        if is_open:
            table_row["status"] = "Occupied"

        orders.append({
            "order_id": order_id,
            "table_id": table_row["table_id"],
            "order_date": order_date,
            "status": status,
        })
        added_orders.append(orders[-1])

        item_id = orderable_ids[i % len(orderable_ids)]
        qty = str((i % 3) + 1)
        lines_for_order = []
        app.merge_line(lines_for_order, app.build_line(menu, order_id, item_id, qty))
        for line in lines_for_order:
            line["unit_price"] = f"{float(line['unit_price']):.2f}"
            line["quantity"] = str(line["quantity"])
        items.extend(lines_for_order)
        added_items.extend(lines_for_order)

    ok = (
        app.save_csv(app.MENU_FILE, app.MENU_FIELDS, menu)
        and app.save_csv(app.TABLE_FILE, app.TABLE_FIELDS, tables)
        and app.save_csv(app.ORDER_FILE, app.ORDER_FIELDS, orders)
        and app.save_csv(app.ITEM_FILE, app.ITEM_FIELDS, items)
    )

    if ok:
        print(f"Added {len(added_menu)} records to each file ({count * 4} total):")
        print(f"  - menu.csv: {len(added_menu)}")
        print(f"  - tables.csv: {len(added_tables)}")
        print(f"  - orders.csv: {len(added_orders)}")
        print(f"  - order_items.csv: {len(added_items)}")
    else:
        print("One or more CSV files failed to save.")


if __name__ == "__main__":
    seed_thirty_five_each(35)