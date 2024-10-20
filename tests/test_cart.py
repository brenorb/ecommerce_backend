import unittest
from app import app

class TestCart(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_add_to_cart(self):
        # First, login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200) 

        # Now add a new product
        add_product_response = self.client.post('/v1/products', json={
            'name': 'Test Product',
            'description': 'This is a test product',
            'price': 10.99,
            'stock': 100
        })
        product_id = add_product_response.get_json()['product']['id']

        # Logout as admin
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)
        
        # Register a new user
        admin_login_response = self.client.post('/v1/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        # If user doesn't already exsists, we need to know the registration succeded
        if admin_login_response.status_code != 409:
            self.assertEqual(admin_login_response.status_code, 200)

        # Login as the new user
        response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)
        user_id = response.get_json()['id']

        # Add a product to the cart
        response = self.client.post('/v1/cart', json={
            'user_id': user_id,
            'product_id': product_id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 201)

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

    def test_get_cart(self):
        # Get products
        products_response = self.client.get('/v1/products')
        self.assertEqual(products_response.status_code, 200)
        products_data = products_response.get_json()
        first_product_id = products_data[0]['id'] if products_data else None
        
        # If there are no products, add one
        if not first_product_id:
            #login as admin
            admin_login_response = self.client.post('/v1/login', json={
                'username': 'admin',
                'password': 'admin_password'
            })
            self.assertEqual(admin_login_response.status_code, 200)

            # Add a new product
            add_product_response = self.client.post('/v1/products', json={
                'name': 'Test Product',
                'description': 'This is a test product',
                'price': 10.99,
                'stock': 100
            })
            self.assertEqual(add_product_response.status_code, 201)
            first_product_id = add_product_response.get_json()['product']['id']

            # Logout as admin
            logout_response = self.client.post('/v1/logout')
            self.assertEqual(logout_response.status_code, 200)  

        # login as the new user
        login_response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 200)
        user_id = login_response.get_json()['id']

        # First, add an item to the cart
        added_cart_item = self.client.post('/v1/cart', json={
            'user_id': user_id,
            'product_id': first_product_id,
            'quantity': 2
        })
        self.assertEqual(added_cart_item.status_code, 201)
        self.assertIn('Item added to cart', added_cart_item.get_json()['message'])
        self.assertIn('id', added_cart_item.get_json()['item'])

        # Now get the cart
        response = self.client.get('/v1/cart/1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertIn('total_price', data)
        self.assertEqual(data['items'][0]['quantity'], 2)

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

    def test_delete_cart(self):
        # Register a new user
        register_response = self.client.post('/v1/register', json={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })

        # Login as the new user
        login_response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 200)
        user_id = login_response.get_json()['id']

        # First, get products
        products_response = self.client.get('/v1/products')
        self.assertEqual(products_response.status_code, 200)
        products_data = products_response.get_json()
        first_product_id = products_data[0]['id'] if products_data else None

        # Add the first product to the cart
        if first_product_id:
            cart_response = self.client.post('/v1/cart', json={
                'user_id': user_id,
                'product_id': first_product_id,
                'quantity': 2
            })
            self.assertEqual(cart_response.status_code, 201)
        else:
            self.assertEqual(cart_response.status_code, 404)

        # Now delete the cart
        response = self.client.delete(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart deleted successfully', response.get_json()['message'])

        # Try to delete again, should say cart is already empty
        response = self.client.delete(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart is already empty', response.get_json()['message'])

        # Verify cart is empty by trying to get it
        response = self.client.get(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart is empty', response.get_json()['message'])

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
