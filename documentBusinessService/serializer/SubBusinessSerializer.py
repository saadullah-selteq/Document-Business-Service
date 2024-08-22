from rest_framework import serializers
from documentBusinessService.models import *


class SubBusinessSerializer(serializers.ModelSerializer):
    businessId = serializers.PrimaryKeyRelatedField(queryset=Business.objects.all())

    class Meta:
        model = SubBusiness
        fields = '__all__'
