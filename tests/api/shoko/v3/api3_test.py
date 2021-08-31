import unittest
from api.shoko.v3.api3 import login_user
from api.shoko.v3.api3models import AuthUser
from unittest.mock import patch


class AuthTests(unittest.TestCase):
    def test_login_user(self):
        mock_get_patcher = patch('api.shoko.v3.api3.login_user')

        login_user_json = {'apikey': '0292fc60-2ba1-4692-941b-d50126810199'}
        login_auth_object = AuthUser(apikey=login_user_json)

        mock_get = mock_get_patcher.start()

        mock_get.return_value = login_auth_object
        response = login_user(user='default', password='', device='unittest')

        mock_get_patcher.stop()

        self.assertEqual(response, login_auth_object)


if __name__ == '__main__':
    unittest.main()
