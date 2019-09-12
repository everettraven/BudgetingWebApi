import requests
import unittest

# Create the unit test class
class API_Tests(unittest.TestCase):

    # Create some variables to use for testing the API
    client_id = "testclientid"
    client_secret = "testclientsecret"
    base_url = "http://localhost:5000"
    authorization_code = ""
    access_token = ""
    refresh_token = ""

    def setUp(self):
        pass

    # Tests registering a new user
    def test_user_register(self):
        data = {"username": "Testing", "password": "Testing"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        r = requests.post(self.base_url + "/user/register", json=data, headers=headers)
        response = r.json()

        self.assertEqual(response['username'], "Testing", "The username should be Tester")
        self.assertEqual(response['spendingLimit'], 0, "spendingLimit should be 0")
        self.assertEqual(len(response['categories']), 0, "Categories should contain nothing")
        self.assertEqual(response['spent'], 0, "spent should be 0")

    # Tests logging in a user
    def test_user_login(self):
        # Register a new user
        reg_data = {"username": "Tester", "password": "Testing"}
        reg_headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        r_reg = requests.post(self.base_url + "/user/register", json=reg_data, headers=reg_headers)

        # Log in the newly registered user
        data = {"username": "Tester", "password": "Testing"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        response = r.json()

        self.assertTrue("authorization_code" in response, "A successful login should return an authorization code")


if __name__ == "__main__":
    unittest.main()






