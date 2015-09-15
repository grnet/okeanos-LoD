from rest_framework import serializers
from .models import LambdaInstance, LambdaApplication, User

# class ApplicationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LambdaApplication
#         fields = ('id', 'description')

class LambdaInstanceSerializer(serializers.ModelSerializer):
    """
    A serializer for LambdaInstance objects.
    """
    class Meta:
        model = LambdaInstance
        fields = ('id', 'uuid', 'name', 'instance_info',
                  'status', 'failure_message',)

class UserSerializer(serializers.ModelSerializer):
    """
    A serializer for User objects.
    """
    lambda_instances = serializers.PrimaryKeyRelatedField(many=True,
                                                          queryset=LambdaInstance.objects.all())

    class Meta:
        model = User
        fields = ('uuid', 'lambda_instances')

class LambdaApplicationSerializer(serializers.ModelSerializer):
    """
    A serializer for LambdaApplication objects.
    """

    class Meta:
        model = LambdaApplication
        fields = ('id', 'description')
