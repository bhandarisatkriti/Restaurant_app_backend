from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, min_length =8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone_number', 'address')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number',''),
            address=validated_data.get('address', '')
        )
        return user