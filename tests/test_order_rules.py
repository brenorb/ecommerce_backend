"""Replays of the Checkout.tla rules on the real Flask routes.

Run from a scratch working directory: the app keeps its database in
data/ecommerce.db relative to the current directory.
"""

import unittest
import uuid

from app import app
from models import Product, db


def product(stock: int) -> int:
    row = db.t.products.insert(Product(id=None, name=f"p-{uuid.uuid4().hex[:6]}", description="test", price=10.0, stock=stock))
    return row["id"] if isinstance(row, dict) else row.id


def stock_of(product_id: int) -> int:
    return db.q("SELECT stock FROM products WHERE id = ?", (product_id,))[0]["stock"]


class TestOrderRules(unittest.TestCase):
    def setUp(self) -> None:
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.user_id = 900_000 + uuid.uuid4().int % 99_999

    def add(self, product_id: int, quantity: int):
        return self.client.post("/v1/cart", json={"user_id": self.user_id, "product_id": product_id, "quantity": quantity})

    def test_placing_an_order_returns_its_id(self) -> None:
        item = product(5)
        self.add(item, 2)
        response = self.client.post(f"/v1/order/{self.user_id}")
        self.assertEqual(response.status_code, 201)
        self.assertIsInstance(response.get_json()["order_id"], int)
        self.assertEqual(stock_of(item), 3)

    def test_a_refused_order_takes_no_stock(self) -> None:
        # Checkout.tla StockConserved: the second item is short, so the
        # order fails, and the first item's stock must be untouched.
        plenty, short = product(5), product(1)
        self.add(plenty, 2)
        self.add(short, 3)
        response = self.client.post(f"/v1/order/{self.user_id}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(stock_of(plenty), 5)
        self.assertEqual(stock_of(short), 1)
