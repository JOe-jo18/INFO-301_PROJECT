# Restaurant Management System

A small, interactive, command-line application for managing restaurant menu items, tables, orders, receipts, and basic sales reports. Data is stored locally in CSV files.

## Features

- **Menu management:** add, list, search by item ID/name/category, update name/price/availability, and remove items.
- **Table management:** list tables and change a table's status between `Available` and `Occupied`.
- **Order management:** create an order for an available table, add available menu items with positive whole-number quantities, and combine repeated items into one order line.
- **Order tracking:** list orders, view receipts, add items to open orders, and mark orders complete. Completing an order makes its table available again.
- **Bills and receipts:** calculate line and order totals and display a receipt using the prices and item names saved with each order.
- **Sales reports:** view a day's orders and completed sales, or totals across all completed orders.
- **CSV persistence:** create any missing data files and their headers automatically.

## Requirements

- Python 3.6 or newer.
- No third-party packages are required; the application and tests use the Python standard library.

## Run

From the project directory, start the interactive application:

```bash
python3 project.py
```

Choose an option from the numbered main menu. Use the submenus to manage menu items, tables, and orders; choose **Exit** to quit.

Run the automated tests with:

```bash
python3 -m unittest -v test
```

## Test checklist

- [Pass] Normal: add, update, search, and remove a menu item.
- [Pass] Normal: change a table status, create an order, add items, and complete it.
- [Pass] Normal: view a receipt and confirm completed-order sales appear in reports.
- [Pass] Normal: run the app twice and confirm CSV-saved records persist.
- [Pass] Invalid: enter menu choices, item IDs, or table IDs that do not exist.
- [Pass] Invalid: enter non-numeric, negative, zero, or decimal quantities.
- [Pass] Invalid: enter negative, non-numeric, empty, or `nan` prices.
- [Pass] Invalid: try to order an unavailable item or add items to a completed order.

The optional `record.py` script adds sample records to the CSV files:

```bash
python3 record.py
```

It adds 35 records to each data file every time it is run, so it is not an idempotent reset/initialization command.

## Data files

The application uses these CSV files in its working directory:

| File | Contents |
| --- | --- |
| `menu.csv` | Menu item IDs, names, categories, prices, and availability |
| `tables.csv` | Table IDs, seat counts, and availability status |
| `orders.csv` | Order IDs, table IDs, dates, and open/completed status |
| `order_items.csv` | Order lines, including a snapshot of item name and unit price |

The repository includes sample data. Back up these files before manually editing or replacing them. Run the application from the project directory so it uses the included data.

## Limitations

- This is a local, single-user console application; it has no graphical interface, login/access controls, network service, or database.
- CSV files do not provide concurrent access or transactional updates. If saving one of several related files fails, some data may already have been written.
- There is no payment processing, tax, tip, discount, inventory tracking, or table-capacity validation.
- Orders can be added to while open or marked complete, but there is no order cancellation, deletion, or editing of saved quantities.
- Completed orders are read-only. Their receipts preserve the item name and price captured when the order line was created; later menu changes do not revise prior receipts.
- Sales totals include completed orders only. The reports are basic summaries, not accounting or financial records.
- Menu categories are entered as text, and table/order data is maintained manually through the application or CSV files.
