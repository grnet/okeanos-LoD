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
        fields = ('uuid', 'name', 'instance_info',
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
        fields = ('uuid', 'description', 'name', 'status', 'failure_message')

class LambdaInstanceInfo(serializers.Serializer):
    """
    Serializer to parse Lambda Instance specs and validate them
    Each of the declared function in this class acts as a validator for the field it refers to in
    its name validator_<field_name>()
    """

    instance_name = serializers.CharField()
    master_name = serializers.CharField()
    project_name = serializers.CharField()
    ip_allocation = serializers.CharField()
    slaves = serializers.IntegerField()
    vcpus_master = serializers.IntegerField()
    vcpus_slave = serializers.IntegerField()
    ram_master = serializers.IntegerField()
    ram_slave = serializers.IntegerField()
    disk_master = serializers.IntegerField()
    disk_slave = serializers.IntegerField()
    network_request = serializers.IntegerField()

    # Allowed values for fields
    allowed = {
        "vcpus":         {8, 1, 2, 4},
        "disks":         {100, 5, 40, 10, 80, 20, 60},
        "ram":           {1024, 2048, 4096, 6144, 8192, 512},
        "disk_types":    {u'drbd', u'ext_vlmc'},
        "ip_allocation": {'all', 'none', 'master'}
    }

    def validate_vcpus_master(self, value):
        if value not in self.allowed['vcpus']:
            raise serializers.ValidationError("Wrong Number of master vcpus")
        return value

    def validate_vcpus_slave(self, value):
        if value not in self.allowed['vcpus']:
            raise serializers.ValidationError("Wrong Number of slave vcpus")
        return value

    def validate_ram_master(self, value):
        if value not in self.allowed['ram']:
            raise serializers.ValidationError("Wrong Amount of master ram")
        return value

    def validate_ram_slave(self, value):
        if value not in self.allowed['ram']:
            raise serializers.ValidationError("Wrong Amount of slave ram")
        return value

    def validate_disk_master(self, value):
        if value not in self.allowed['disks']:
            raise serializers.ValidationError("Wrong Size of master disk")
        return value

    def validate_disk_slave(self, value):
        if value not in self.allowed['disks']:
            raise serializers.ValidationError("Wrong Size of slave disk")
        return value

    def validate_ip_allocation(self, value):
        if value not in self.allowed['ip_allocation']:
            raise serializers. \
                ValidationError("Wrong choise for ip_allocation, "
                                "available choices {}".format(self.allowed['ip_allocation']))
        return value

    def validate(self, data):
        return data