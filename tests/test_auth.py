import unittest
from app import app
import os
from dotenv import load_dotenv

load_dotenv()

class TestAuth(unittest.TestCase):

    def setUp(self) -> None:
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_login(self) -> None:
        response = self.client.post('/v1/login', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
        })
        self.assertEqual(response.status_code, 200)

    def test_logout(self) -> None:
        # First, login
        login_response = self.client.post('/v1/login', json={
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
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

    def test_delete_own_account(self) -> None:
        # First, register a user
        self.client.post('/v1/register', json={
            'username': os.getenv('DELETE_USER_USERNAME', 'deleteuser'),
            'password': os.getenv('DELETE_USER_PASSWORD', 'testpass'),
            'email': 'delete@example.com'
        })

        # Now login the user
        login_response = self.client.post('/v1/login', json={
            'username': os.getenv('DELETE_USER_USERNAME', 'deleteuser'),
            'password': os.getenv('DELETE_USER_PASSWORD', 'testpass')
        })
        self.assertEqual(login_response.status_code, 200)

        # Now delete the user's own account
        delete_response = self.client.delete('/v1/user/deleteuser')
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn('User account deleted successfully', delete_response.get_json()['message'])

        # Try to login again, should fail
        login_response = self.client.post('/v1/login', json={
            'username': os.getenv('DELETE_USER_USERNAME', 'deleteuser'),
            'password': os.getenv('DELETE_USER_PASSWORD', 'testpass')
        })
        self.assertEqual(login_response.status_code, 401)
        self.assertIn('Unauthorized', login_response.get_json()['error'])

if __name__ == '__main__':
    unittest.main()
