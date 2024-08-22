from rest_framework import serializers
from documentBusinessService.models import *


class BusinessFileSerializer(serializers.ModelSerializer):
    folderId = serializers.PrimaryKeyRelatedField(queryset=DocumentBusinessFolder.objects.all())

    class Meta:
        model = DocumentBusinessFile
        fields = '__all__'
