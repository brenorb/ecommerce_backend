import unittest
from app import app

class TestProduct(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_get_product_by_id(self):
        # First, login as admin to add a product for testing
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

        # Add a product to retrieve
        add_product_response = self.client.post('/v1/products', json={
            'name': 'Test Product',
            'description': 'This is a test product.',
            'price': 19.99,
            'stock': 100
        })
        self.assertEqual(add_product_response.status_code, 201)
        product_id = add_product_response.get_json()['product']['id']

        # Logout as admin
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

        # Now login as a regular user to retrieve the product
        login_response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(login_response.status_code, 200)

        # Retrieve the product by ID
        get_product_response = self.client.get(f'/v1/products/{product_id}')
        self.assertEqual(get_product_response.status_code, 200)
        self.assertIn('Test Product', get_product_response.get_json()[0]['name'])

        # Try to get a non-existing product
        get_non_existing_response = self.client.get('/v1/products/9999999999')
        self.assertEqual(get_non_existing_response.status_code, 404)
        self.assertIn('Product not found', get_non_existing_response.get_json()['error'])

        # Logout as regular user
        logout_response = self.client.post('/v1/logout')
        self.assertEqual(logout_response.status_code, 200)

        # Login as admin again
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

        # Delete the product
        delete_product_response = self.client.delete(f'/v1/products/{product_id}')
        self.assertEqual(delete_product_response.status_code, 200)
        self.assertIn('Product deleted successfully', delete_product_response.get_json()['message'])

        # Logout as admin
        logout_response = self.client.post('/v1/logout')        
        self.assertEqual(logout_response.status_code, 200)

    def test_add_product(self):
        # First, login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

        # Now attempt to add a product
        add_product_response = self.client.post('/v1/products', json={
            'name': 'Test Product',
            'description': 'This is a test product.',
            'price': 19.99,
            'stock': 100
        })
        self.assertEqual(add_product_response.status_code, 201)
        self.assertIn('Product added successfully', add_product_response.get_json()['message'])

    def test_update_product(self):
        # First, login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

        # Add a product to update
        add_product_response = self.client.post('/v1/products', json={
            'name': 'Update Product',
            'description': 'This product will be updated.',
            'price': 29.99,
            'stock': 50
        })
        self.assertEqual(add_product_response.status_code, 201)

        # Now update the product
        product_id = add_product_response.get_json()['product']['id'] 
        update_product_response = self.client.put(f'/v1/products/{product_id}', json={
            'name': 'Updated Product',
            'description': 'This product has been updated.',
            'price': 39.99,
            'stock': 75
        })
        self.assertEqual(update_product_response.status_code, 200)
        self.assertIn('Product updated successfully', update_product_response.get_json()['message'])

        # Try to update a non-existing product
        update_non_existing_response = self.client.put('/v1/products/999', json={
            'name': 'Non-existing Product',
            'description': 'This product does not exist.',
            'price': 49.99,
            'stock': 0
        })
        self.assertEqual(update_non_existing_response.status_code, 404)
        self.assertIn('Product not found', update_non_existing_response.get_json()['error'])

    def test_delete_product(self):
        # First, login as admin
        admin_login_response = self.client.post('/v1/login', json={
            'username': 'admin',
            'password': 'admin_password'
        })
        self.assertEqual(admin_login_response.status_code, 200)

        # Add a product to delete
        add_product_response = self.client.post('/v1/products', json={
            'name': 'Delete Product',
            'description': 'This product will be deleted.',
            'price': 9.99,
            'stock': 10
        })
        self.assertEqual(add_product_response.status_code, 201)
        product_id = add_product_response.get_json()['product']['id']

        # Now delete the product
        delete_product_response = self.client.delete(f'/v1/products/{product_id}')
        self.assertEqual(delete_product_response.status_code, 200)
        self.assertIn('Product deleted successfully', delete_product_response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
