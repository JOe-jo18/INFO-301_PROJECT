"""Automated tests: bill totals, invalid quantities, unavailable items, CSV persistence."""  # Describes the file
import os  # File-path helpers
import tempfile  # Creates a throw-away folder so real data is never touched
import unittest  # Built-in testing framework

import project as r  # Import our program (main() does not run on import)

MENU = [  # Small fake menu used by the tests
    {"item_id": "M001", "name": "Jollof Rice", "category": "Main", "price": "8.50", "available": "Yes"},  # Available
    {"item_id": "M002", "name": "Lobster", "category": "Main", "price": "25.00", "available": "No"},  # Unavailable
]  # End of menu


class TestBill(unittest.TestCase):  # Groups bill-calculation tests
    def test_line_total(self):  # 8.50 x 3 = 25.50
        self.assertEqual(r.line_total("8.50", 3), 25.50)  # Compare result

    def test_order_total(self):  # Sum of two lines
        lines = [{"unit_price": "8.50", "quantity": "2"}, {"unit_price": "3.00", "quantity": "1"}]  # 17 + 3
        self.assertEqual(r.order_total(lines), 20.00)  # Expected 20.00

    def test_empty_order_total(self):  # No lines means zero
        self.assertEqual(r.order_total([]), 0)  # Expected 0


class TestQuantity(unittest.TestCase):  # Groups quantity validation tests
    def test_valid(self):  # Normal case
        self.assertEqual(r.parse_quantity("4"), 4)  # "4" becomes 4

    def test_invalid_values(self):  # Every bad value must raise ValueError
        for bad in ["0", "-1", "abc", "2.5", ""]:  # Zero, negative, text, decimal, empty
            with self.subTest(bad=bad):  # Report which value failed
                with self.assertRaises(ValueError):  # Expect an error
                    r.parse_quantity(bad)  # Call the function


class TestPrice(unittest.TestCase):  # Groups price validation tests
    def test_valid(self):  # Normal and zero prices are fine
        self.assertEqual(r.parse_price("4.5"), 4.5)  # Decimal price
        self.assertEqual(r.parse_price("0"), 0)  # Zero is allowed

    def test_invalid(self):  # Bad prices
        for bad in ["-1", "abc", "nan", ""]:  # Negative, text, nan, empty
            with self.subTest(bad=bad):  # Report which value failed
                with self.assertRaises(ValueError):  # Expect an error
                    r.parse_price(bad)  # Call the function


class TestOrdering(unittest.TestCase):  # Groups order-line tests
    def test_available_item(self):  # Valid order line
        line = r.build_line(MENU, "O001", "M001", "2")  # Order 2 Jollof Rice
        self.assertEqual(line["quantity"], 2)  # Quantity stored
        self.assertEqual(line["unit_price"], "8.50")  # Price copied

    def test_unavailable_item(self):  # Rule: unavailable items cannot be ordered
        with self.assertRaises(ValueError):  # Expect an error
            r.build_line(MENU, "O001", "M002", "1")  # Lobster is unavailable

    def test_unknown_item(self):  # Non-existing ID
        with self.assertRaises(ValueError):  # Expect an error
            r.build_line(MENU, "O001", "M999", "1")  # ID does not exist

    def test_zero_quantity(self):  # Rule: quantity must be positive
        with self.assertRaises(ValueError):  # Expect an error
            r.build_line(MENU, "O001", "M001", "0")  # Quantity zero

    def test_merge_same_item(self):  # Ordering the same item twice adds quantities
        lines = []  # Start empty
        r.merge_line(lines, r.build_line(MENU, "O001", "M001", "2"))  # First add
        r.merge_line(lines, r.build_line(MENU, "O001", "M001", "3"))  # Second add
        self.assertEqual(len(lines), 1)  # Still one line
        self.assertEqual(lines[0]["quantity"], 5)  # 2 + 3


class TestIdsAndSearch(unittest.TestCase):  # Groups ID and search tests
    def test_next_id(self):  # Highest number + 1
        rows = [{"order_id": "O001"}, {"order_id": "O007"}]  # Existing IDs
        self.assertEqual(r.next_id(rows, "order_id", "O", 3), "O008")  # Next is O008

    def test_next_id_empty(self):  # First record
        self.assertEqual(r.next_id([], "order_id", "O", 3), "O001")  # Starts at 1

    def test_find_existing_and_missing(self):  # Search by ID
        self.assertIsNotNone(r.find_row(MENU, "item_id", "m001"))  # Case-insensitive match
        self.assertIsNone(r.find_row(MENU, "item_id", "M999"))  # Missing returns None


class TestCsv(unittest.TestCase):  # Groups persistence tests
    def test_save_then_load(self):  # Data survives a "restart" (re-reading the file)
        with tempfile.TemporaryDirectory() as folder:  # Temporary folder
            path = os.path.join(folder, "menu.csv")  # Temp file path
            r.save_csv(path, r.MENU_FIELDS, MENU)  # Save
            self.assertEqual(r.load_csv(path, r.MENU_FIELDS), MENU)  # Load gives same data

    def test_missing_file_created_with_header(self):  # File auto-created
        with tempfile.TemporaryDirectory() as folder:  # Temporary folder
            path = os.path.join(folder, "new.csv")  # File does not exist yet
            self.assertEqual(r.load_csv(path, r.MENU_FIELDS), [])  # Empty list returned
            with open(path, encoding="utf-8") as f:  # Re-open the created file
                self.assertEqual(f.readline().strip(), ",".join(r.MENU_FIELDS))  # Header exists


if __name__ == "__main__":  # Run tests when executed directly
    unittest.main()  # Start unittest