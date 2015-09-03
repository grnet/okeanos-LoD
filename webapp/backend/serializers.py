from rest_framework import serializers
from .models import ProjectFile, LambdaInstance, Server, PrivateNetwork


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ('id', 'name', 'description')


class ServerSerializer(serializers.ModelSerializer):
    """
    A serializer for Server objects.
    """

    class Meta:
        model = Server
        fields = ('id', 'hostname', 'cpus', 'ram', 'disk', 'pub_ip', 'pub_id_id', 'priv_ip')


class PrivateNetworkSerializer(serializers.ModelSerializer):
    """
    A serializer for PrivateNetwork objects.
    """

    class Meta:
        model = PrivateNetwork
        fields = ('id', 'subnet', 'gateway')


class LambdaInstanceSerializer(serializers.ModelSerializer):
    """
    A serializer for LambdaInstance objects.
    """

    servers = ServerSerializer(many=True)
    private_network = PrivateNetworkSerializer()

    class Meta:
        model = LambdaInstance
        fields = ('id', 'uuid', 'name', 'instance_info', 'status', 'failure_message', 'servers',
                  'private_networks')
