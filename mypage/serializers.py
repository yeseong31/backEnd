from rest_framework import serializers

from common.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

# 위 코드는 0528 기준 사용하지 않음
