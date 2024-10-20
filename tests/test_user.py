import unittest
from app import app

class TestUser(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

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

if __name__ == '__main__':
    unittest.main()
