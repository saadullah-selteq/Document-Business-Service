from rest_framework import serializers
from documentBusinessService.models import *


class BusinessFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentBusinessFolder
        fields = '__all__'
