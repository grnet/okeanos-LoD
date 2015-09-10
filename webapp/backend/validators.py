from rest_framework.serializers import ValidationError


class LambdaInfoValidator(object):
    def __init__(self):
        pass

    def __call__(self, value):
        if not value:
            raise ValidationError

    def set_context(self, serializer_field):
        self.parent = serializer_field.parent