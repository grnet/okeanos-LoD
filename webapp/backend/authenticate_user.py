import json

from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.hashers import make_password

from django.utils import timezone
import requests

from fokia.utils import check_auth_token
from .models import Token, User
from .exceptions import CustomAuthenticationFailed


class OldTokenException(Exception):
    pass


class KamakiTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        hashed_token_key = make_password(key)
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
                    token.creation_date = timezone.now()
                    token.save()
            else:
                raise CustomAuthenticationFailed()
        return token.user, token


def get_public_key(auth_token):
    headers = {"Content-Type": "application/json",
               "Accept":       "application/json",
               "X-Auth-Token": auth_token}
    req = requests.get(url="https://cyclades.okeanos.grnet.gr/userdata/keys",
                       headers=headers)
    user_keys = json.loads(req.content)
    return user_keys


def get_named_keys(auth_token, names=[]):
    user_keys = get_public_key(auth_token=auth_token)
    keys = []
    for key in user_keys:
        if key['name'] in names:
            keys.append(key['content'])
    return keys
