import unittest
from app import app

class TestAuth(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_login(self):
        response = self.client.post('/v1/login', json={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 200)

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
