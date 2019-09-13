import requests
import unittest

# Create the unit test class
class API_Tests(unittest.TestCase):

    # Create some variables to use for testing the API
    client_id = "testclientid"
    client_secret = "testclientsecret"
    base_url = "http://localhost:5000"

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
        data = {"username": "Tester", "password": "Testing"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        r_reg = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Log in the newly registered user
        r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        response = r.json()

        self.assertTrue("authorization_code" in response, "A successful login should return an authorization code")

    def test_developer_register(self):
        data = {"name": "TestDeveloper", "redirect_uri": "www.TestDeveloper.com"}
        headers = {"Content-Type": "application/json"}
        r = requests.post(self.base_url + "/developer/register", json=data, headers=headers)
        response = r.json()

        self.assertEqual(response["name"], "TestDeveloper", "The name of the developer should be TestDeveloper")
        self.assertEqual(response["redirect_uri"], "www.TestDeveloper.com", "The redirect_uri should be www.TestDeveloper.com")
        self.assertTrue("client_id" in response, "client_id should be in the JSON response")
        self.assertTrue("client_secret" in response, "client_secret should be in the JSON response")
    
    def test_user_auth_code(self):
        auth_code = ""
        
        # Register a new user
        data = {"username": "AuthCodeTester", "password": "AuthCodeTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        self.assertTrue("access_token" in auth_resp, "access_token should be in the JSON response")
        self.assertTrue("refresh_token" in auth_resp, "refresh_token should be in the JSON response")


    def test_user_auth_refresh(self):
        auth_code = ""
        refresh_token = ""

        # Register a new user
        data = {"username": "AuthRefreshTester", "password": "AuthRefreshTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        refresh_token = auth_resp["refresh_token"]

        ref_headers = {"Authorization": "Bearer " + str(refresh_token), "client_id": self.client_id, "client_secret": self.client_secret}
        ref_r = requests.post(self.base_url + "/user/auth", headers=ref_headers)
        ref_resp = ref_r.json()

        self.assertTrue("access_token" in ref_resp, "access_token should be in the JSON response")

    def test_category_add(self):
        auth_code = ""
        access_token = ""
        
        # Register a new user
        data = {"username": "CatAddTester", "password": "CatAddTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        access_token = auth_resp["access_token"]

        cat_data = {"name": "Gas"}
        cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        cat_r = requests.post(self.base_url + "/user/categories/add", json=cat_data, headers=cat_headers)
        cat_resp = cat_r.json()

        self.assertEqual(cat_resp["categories"][0]["name"], "Gas", "The added category name should be Gas.")
        self.assertTrue(len(cat_resp["categories"]) == 1, "The length of the categories section should be 1")
        self.assertTrue("expenses" in cat_resp["categories"][0], "expenses should be in the JSON response.")
        self.assertTrue(len(cat_resp["categories"][0]["expenses"]) == 0, "The length of expenses should be 0")
        self.assertTrue("id" in cat_resp["categories"][0], "id should be in the JSON response")

    def test_category_get(self):
        auth_code = ""
        access_token = ""
        
        # Register a new user
        data = {"username": "CatGetTester", "password": "CatGetTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        access_token = auth_resp["access_token"]

        cat_data = {"name": "Gas"}
        cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        cat_r = requests.post(self.base_url + "/user/categories/add", json=cat_data, headers=cat_headers)
        
        cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret}
        cat_r = requests.get(self.base_url + "/user/categories", headers=cat_headers)
        cat_resp = cat_r.json()

        self.assertTrue(len(cat_resp) == 1, "The length of the categories section should be 1")
        self.assertTrue("expenses" in cat_resp[0], "expenses should be in the JSON response.")
        self.assertTrue(len(cat_resp[0]["expenses"]) == 0, "The length of expenses should be 0")
        self.assertTrue("id" in cat_resp[0], "id should be in the JSON response")

    def test_category_get_multiple(self):
        auth_code = ""
        access_token = ""
        
        # Register a new user
        data = {"username": "CatGetMultTester", "password": "CatGetMultTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        access_token = auth_resp["access_token"]

        for i in range(4):
            cat_data = {"name": "Gas" + str(i)}
            cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
            cat_r = requests.post(self.base_url + "/user/categories/add", json=cat_data, headers=cat_headers)
            
        cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret}
        cat_r = requests.get(self.base_url + "/user/categories", headers=cat_headers)
        cat_resp = cat_r.json()

        self.assertTrue(len(cat_resp) == 4, "The length of the categories section should be 4")


    def test_category_get_id(self):
        auth_code = ""
        access_token = ""
        id_to_get = 0;
        
        # Register a new user
        data = {"username": "CatGetIdTester", "password": "CatGetIdTester"}
        headers = {"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
        reg_r = requests.post(self.base_url + "/user/register", json=data, headers=headers)

        # Login as new user
        login_r = requests.post(self.base_url + "/user/login", json=data, headers=headers)
        login_resp = login_r.json()
        auth_code = login_resp["authorization_code"]

        # Exchange auth_code for access_token and refresh_token
        auth_data = {"code": auth_code}
        auth_r = requests.post(self.base_url + "/user/auth", json=auth_data, headers=headers)
        auth_resp = auth_r.json()

        access_token = auth_resp["access_token"]

        for i in range(3):
            cat_data = {"name": "Gas" + str(i)}
            cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret, "Content-Type": "application/json"}
            cat_r = requests.post(self.base_url + "/user/categories/add", json=cat_data, headers=cat_headers)
            if i == 1:
                cat_resp = cat_r.json()
                id_to_get = cat_resp["categories"][1]["id"]
            
        cat_headers = {"Authorization": "Bearer " + str(access_token) ,"client_id": self.client_id, "client_secret": self.client_secret}
        cat_r = requests.get(self.base_url + "/user/categories/" + str(id_to_get), headers=cat_headers)
        cat_resp = cat_r.json()

        self.assertEqual(cat_resp["name"], "Gas1", "The name of the category with the specified id should be Gas1")
        self.assertEqual(cat_resp["id"], id_to_get, "The id of the item gotten should be " + str(id_to_get))


if __name__ == "__main__":
    unittest.main()






