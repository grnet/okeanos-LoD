from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from fokia.utils import check_auth_token

from .models import Token, User

from django.conf import settings

from .exceptions import CustomAuthenticationFailed


class OldTokenException(Exception):
    """
    Exception class signifying that the authentication token inside the database
    to which the user was matched is more than X days old, in which case a cross-reference
    with Kamaki is needed.
    """
    pass


class KamakiTokenAuthentication(TokenAuthentication):
    """
    Token authentication class for restricing access to the LoD Central Service API.
    """

    # Model against which the authentication is made.
    model = Token

    def authenticate_credentials(self, key):
        """
        The actual authentication method.
        :param key: Key is the token passed from the user.
        :return: Tuple with the owner of the token (User) and their respective token.
        """
        hashed_token_key = make_password(key, salt=settings.STATIC_SALT)
        try:
            token = self.model.objects.get(key=hashed_token_key)
            if timezone.now() > token.creation_date + timezone.timedelta(days=5):
                raise OldTokenException
        except (self.model.DoesNotExist, OldTokenException):
            status, info = check_auth_token(key)
            if status:
                uuid = info['access']['user']['id']
                if User.objects.filter(uuid=uuid).count() == 0:
                    user = User.objects.create(uuid=uuid)
                else:
                    user = User.objects.get(uuid=uuid)

                if Token.objects.filter(user=user).count() == 0:
                    token = Token.objects.create(user=user, key=hashed_token_key,
                                                 creation_date=timezone.now())
                else:
                    token = Token.objects.get(user=user)
                    token.key = hashed_token_key
                    token.save()
            else:
                raise CustomAuthenticationFailed()
        return token.user, token
