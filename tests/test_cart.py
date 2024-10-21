import unittest
from app import app
import os
from dotenv import load_dotenv

load_dotenv()

class TestCart(unittest.TestCase):

    def setUp(self) -> None:
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_add_to_cart(self) -> None:
        # First, login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': os.getenv('ADMIN_USERNAME'),
            'password': os.getenv('ADMIN_PASSWORD')
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
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass'),
            'email': 'test@example.com'
        })
        # If user doesn't already exist, we need to know the registration succeeded
        if admin_login_response.status_code != 409:
            self.assertEqual(admin_login_response.status_code, 200)

        # Login as the new user
        response = self.client.post('/v1/login', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
        })
        self.assertEqual(response.status_code, 200)
        user_id = response.get_json()['id']

        # Clear the cart
        response = self.client.delete(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(response.get_json()['message'], ['Cart deleted successfully', 'Cart is already empty'])
  
        # Add a product to the cart
        response = self.client.post('/v1/cart', json={
            'user_id': user_id,
            'product_id': product_id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 201)

        # Now update the quantity
        response = self.client.post('/v1/cart', json={
            'user_id': user_id,
            'product_id': product_id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, 200)

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

    def test_get_cart(self) -> None:
        # Get products
        products_response = self.client.get('/v1/products')
        self.assertEqual(products_response.status_code, 200)
        products_data = products_response.get_json()
        first_product_id = products_data[0]['id'] if products_data else None
        
        # If there are no products, add one
        if not first_product_id:
            #login as admin
            admin_login_response = self.client.post('/v1/login', json={
                'username': os.getenv('ADMIN_USERNAME'),
                'password': os.getenv('ADMIN_PASSWORD')
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
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
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
        response = self.client.get(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('items', data)
        self.assertIn('total_price', data)
        self.assertEqual(data['items'][0]['quantity'], 2)

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

    def test_delete_cart(self) -> None:
        # Register a new user
        register_response = self.client.post('/v1/register', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass'),
            'email': 'test@example.com'
        })

        # Login as the new user
        login_response = self.client.post('/v1/login', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
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

    def test_place_order(self) -> None:
        # Register a new user
        register_response = self.client.post('/v1/register', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass'),
            'email': 'test@example.com'
        })

        # Login as the new user
        login_response = self.client.post('/v1/login', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
        })
        self.assertEqual(login_response.status_code, 200)
        user_id = login_response.get_json()['id']

        # Get products
        products_response = self.client.get('/v1/products')
        self.assertEqual(products_response.status_code, 200)
        products_data = products_response.get_json()
        first_product_id = products_data[0]['id'] if products_data else None
        product_stock = products_data[0]['stock'] if products_data else None

        # Delete cart
        response = self.client.delete(f'/v1/cart/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart deleted successfully', response.get_json()['message'])

        # Add the first product to the cart
        if not first_product_id:
            self.fail("No products available to add to the cart.")

        quant = 2
        cart_response = self.client.post('/v1/cart', json={
            'user_id': user_id,
            'product_id': first_product_id,
            'quantity': quant
        })
        self.assertIn(cart_response.status_code, [200, 201])

        # Now place an order
        order_response = self.client.post(f'/v1/order/{user_id}')
        self.assertEqual(order_response.status_code, 201)
        self.assertIn('Order placed successfully', order_response.get_json()['message'])

        # Verify that the cart is now empty
        cart_response = self.client.get(f'/v1/cart/{user_id}')
        self.assertEqual(cart_response.status_code, 200)
        self.assertIn('Cart is empty', cart_response.get_json()['message'])

        # Check if the product stock is updated
        product_response = self.client.get(f'/v1/products/{first_product_id}')
        self.assertEqual(product_response.status_code, 200)
        self.assertEqual(product_response.get_json()[0]['stock'], product_stock - quant)

        # Logout as the new user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
