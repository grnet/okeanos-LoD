from rest_framework import serializers
from .models import ProjectFile


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ('name', 'path', 'description')
