from rest_framework import serializers
from .models import CustomAdminUser, EmissionReductionTip

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAdminUser
        fields = ('id', 'username', 'email', 'password', 'is_active')
        extra_kwargs = {'email': {'required': True, 'write_only': True}, 'password': {'write_only': True}}


class EmissionReductionTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmissionReductionTip
        fields = '__all__'
