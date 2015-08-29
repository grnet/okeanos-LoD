from rest_framework.authentication import TokenAuthentication
from rest_framework.views import exceptions

from .models import Token


class KamakiTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        return token.user, token
