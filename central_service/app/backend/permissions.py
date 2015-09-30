from django.contrib.auth.hashers import make_password
from .models import User
from rest_framework.permissions import BasePermission, SAFE_METHODS


# Custom permission classes. To be used in the future.
class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        token = request["HTTP_AUTHORIZATION"][-1]
        hashed_token = make_password(key=token)
        request_user = User.objects.filter(kamaki_token__key__eq=hashed_token)
        return obj.owner == request_user


class IsOwnerOrReadOnly(IsOwner):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return super(IsOwnerOrReadOnly, self).has_object_permission(request, view, obj)
