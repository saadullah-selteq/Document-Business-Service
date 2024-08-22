from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import *

class FolderSerlizer(serializers.ModelSerializer):
     class Meta:
        model = documentFolder
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    folderId = serializers.PrimaryKeyRelatedField(queryset=documentFolder.objects.all())
    class Meta:
        model = documentFile
        fields = '__all__'

class UserStorageSerlizer(serializers.ModelSerializer):
     class Meta:
        model = customer
        fields = '__all__'