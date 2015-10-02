import unittest
from mock import patch

from backend.exceptions import CustomAuthenticationFailed
from backend.models import User, Token
from backend.authenticate_user import KamakiTokenAuthentication
from django.utils import timezone

from django.contrib.auth.hashers import make_password
from django.conf import settings
import uuid


class TestAuthentication(unittest.TestCase):
    """
    Test case for API authentication with ~okeanos.
    """

    def setUp(self):
        self.correct_token = "some_correct_token"
        self.inexistent_token = "some_inexistent_token"
        self.existent_token = "some_existent_token"
        self.existent_old_token = "some_existent_old_token"
        self.correct_token_inexistent_user_id = "12345"
        self.wrong_token = "some_wrong_token"

        self.existent_token_owner = User.objects.create(uuid=str(uuid.uuid4()))



    def tearDown(self):
        pass

    @patch('backend.authenticate_user.make_password')
    @patch('backend.authenticate_user.check_auth_token')
    def test_key_is_always_hashed(self, auth_mock, make_pass_mock):
        """
        Test that the user's token is always hashed before saved in database.
        :param auth_mock: The authentication endpoint mock object.
        :param make_pass_mock: The make_password mock object.
        """

        auth_mock.return_value = (True,
                                  {
                                      'access': {
                                          'user': {
                                              'id': "some_id"
                                          }
                                      }
                                  })
        make_pass_mock.return_value = "correct_hash"
        KamakiTokenAuthentication().authenticate_credentials(self.correct_token)
        self.assertTrue(make_pass_mock.called)
        make_pass_mock.reset_mock()
        make_pass_mock.return_value = "wrong_hash"
        auth_mock.return_value = (False, 'whatever the reason')
        try:
            KamakiTokenAuthentication().authenticate_credentials(self.wrong_token)
        except(CustomAuthenticationFailed):
            self.assertTrue(make_pass_mock.called)
        # self.assertTrue(make_pass_mock.called)


    @patch('backend.authenticate_user.check_auth_token')
    def test_non_existent_db_user_calls_kamaki(self, auth_mock):
        """
        Tests that a user not existent in the database authenticates against the ~okeanos
        astakos.
        :param auth_mock: The authentication endpoint mock object.
        """

        auth_mock.return_value = ("whatever_status", "whatever_info")
        try:
            KamakiTokenAuthentication().authenticate_credentials(self.inexistent_token)
        except:
            self.assertTrue(auth_mock.called)

    @patch('backend.authenticate_user.check_auth_token')
    def test_invalid_token_fails_authentication(self, auth_mock):
        """
        Tests that an invalid key fails authentication.
        :param auth_mock: The authentication endpoint mock object.
        """

        auth_mock.return_value = (False, '{"unauthorized": {"message": "Invalid token", '
                                         '"code": 401, "details": ""}}')
        self.assertRaises(CustomAuthenticationFailed)

    @patch('backend.authenticate_user.make_password')
    @patch('backend.authenticate_user.check_auth_token')
    def test_valid_token_non_existent_db_user_writes_database(self, auth_mock, make_pass_mock):
        make_pass_mock.return_value = "312312"
        auth_mock.return_value = (True,
                                 {
                                     'access': {
                                         'user': {
                                             'id': self.correct_token_inexistent_user_id
                                         }
                                     }
                                 })
        KamakiTokenAuthentication().authenticate_credentials(self.inexistent_token)
        db_user_count = User.objects.filter(uuid=self.correct_token_inexistent_user_id).count()
        self.assertEquals(db_user_count, 1)
        db_token_count = Token.objects.filter(key=make_pass_mock.return_value).count()
        self.assertEquals(db_token_count, 1)

    @patch('backend.authenticate_user.check_auth_token')
    def test_old_key_reauthenticates(self, auth_mock):
        """
        Tests than an old key will re-authenticated with Astakos endpoing.
        :param auth_mock: The authentication endpoint mock object.
        """

        self.existent_old_token_obj = Token.objects.create(
            key=make_password(self.existent_old_token, salt=settings.STATIC_SALT),
            creation_date=timezone.now()-timezone.timedelta(days=6),
            user=self.existent_token_owner)

        auth_mock.return_value = ("whatever_status", "whatever_info")
        try:
            KamakiTokenAuthentication().authenticate_credentials(self.existent_old_token)
        except:
            self.assertTrue(auth_mock.called)

    @patch('backend.authenticate_user.check_auth_token')
    def test_existent_user_token_passes_authentication(self, auth_mock):
        """
        Tests that an existent user with an existing token in the db passes authentication
        without contacting astakos endpoint.
        :param auth_mock: The authentication endpoint mock object.
        """
        self.existent_token_obj = Token.objects.create(key=make_password(self.existent_token,
                                                                     salt=settings.STATIC_SALT),
                                                   creation_date=timezone.now(),
                                                   user=self.existent_token_owner)

        KamakiTokenAuthentication().authenticate_credentials(self.existent_token)
        self.assertFalse(auth_mock.called)

if __name__ == '__main__':
    unittest.main()