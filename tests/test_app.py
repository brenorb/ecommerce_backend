import unittest
from app import app
from flask.testing import FlaskClient

class TestEcommerceBackend(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h1>Hello, World</h1>", response.data)

    def test_register(self):
        # First, delete the test user if it exists
        self.client.delete('/v1/user/testuser')

        # Now attempt to register the user
        response = self.client.post('/v1/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)

    def test_get_products(self):
        response = self.client.get('/v1/products')
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        response = self.client.post('/v1/cart', json={
            'user_id': 1,
            'product_id': 1,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 201)

    def test_place_order(self):
        response = self.client.post('/v1/order', json={
            'user_id': 1,
            'cart_id': 1
        })
        self.assertEqual(response.status_code, 201)

    def test_delete_user(self):
        # First, register a user
        self.client.post('/v1/register', json={
            'username': 'deleteuser',
            'password': 'testpass',
            'email': 'delete@example.com'
        })

        # Now delete the user
        response = self.client.delete('/v1/user/deleteuser')
        self.assertEqual(response.status_code, 200)

        # Try to delete again, should get 404
        response = self.client.delete('/v1/user/deleteuser')
        self.assertEqual(response.status_code, 404)

    def test_get_cart(self):
        # First, add an item to the cart
        self.client.post('/v1/cart', json={
            'user_id': 1,
            'product_id': 1,
            'quantity': 2
        })

        # Now get the cart
        response = self.client.get('/v1/cart/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertIn('total_price', data)
        self.assertEqual(len(data['items']), 1)
        self.assertEqual(data['items'][0]['quantity'], 2)

    def test_delete_cart(self):
        # First, add an item to the cart
        self.client.post('/v1/cart', json={
            'user_id': 1,
            'product_id': 1,
            'quantity': 2
        })

        # Now delete the cart
        response = self.client.delete('/v1/cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart deleted successfully', response.get_json()['message'])

        # Try to delete again, should say cart is already empty
        response = self.client.delete('/v1/cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart is already empty', response.get_json()['message'])

        # Verify cart is empty by trying to get it
        response = self.client.get('/v1/cart/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart is empty', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
