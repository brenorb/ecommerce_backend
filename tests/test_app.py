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
        self.assertIn(b"API running", response.data)

    def test_register(self):
        # First, check if the test user exists
        check_user_response = self.client.get('/v1/user/testuser')
        if check_user_response.status_code == 200:
            # Login as admin
            admin_login_response = self.client.post('/v1/login', json={
                'username': 'admin',
                'password': 'admin_password'
            })
            self.assertEqual(admin_login_response.status_code, 200)
            # Delete the test user
            delete_user_response = self.client.delete('/v1/user/testuser')
            self.assertEqual(delete_user_response.status_code, 200)
            # Logout
            logout_response = self.client.post('/v1/logout')
            self.assertEqual(logout_response.status_code, 200)

        # Now attempt to register the user
        register_response = self.client.post('/v1/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com',
            'is_admin': False  
        })
        self.assertEqual(register_response.status_code, 201)
        self.assertIn('User registered successfully', register_response.get_json()['message'])

        # Try to register the same user again, should fail
        duplicate_register_response = self.client.post('/v1/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.assertEqual(duplicate_register_response.status_code, 409)
        self.assertIn('Conflict: username or email already exists', duplicate_register_response.get_json()['error'])

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
        # Register a user
        self.client.post('/v1/register', json={
            'username': 'deleteuser',
            'password': 'testpass',
            'email': 'delete@example.com'
        })

        # Login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

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

    def test_logout(self):
        # First, login
        login_response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 200)
        
        # Now logout
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn('Logged out successfully', logout_response.get_json()['message'])
        
        # Try to logout again, should get a message that no user is logged in
        second_logout_response = self.client.post('/v1/logout')
        self.assertEqual(second_logout_response.status_code, 400)
        self.assertIn('No user is currently logged in', second_logout_response.get_json()['message'])

    def test_delete_own_account(self):
        # First, register a user
        self.client.post('/v1/register', json={
            'username': 'deleteuser',
            'password': 'testpass',
            'email': 'delete@example.com'
        })

        # Now login the user
        login_response = self.client.post('/v1/login', json={
            'username': 'deleteuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 200)

        # Now delete the user's own account
        delete_response = self.client.delete('/v1/user/deleteuser')
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn('User account deleted successfully', delete_response.get_json()['message'])

        # Try to login again, should fail
        login_response = self.client.post('/v1/login', json={
            'username': 'deleteuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 401)
        self.assertIn('Unauthorized', login_response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
