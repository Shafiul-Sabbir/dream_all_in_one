from rest_framework import serializers
from payments.models import Traveller


class TravellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveller
        fields = '__all__'

    def create(self, validated_data):
        # Custom logic for creating a Traveller instance
        password = validated_data.pop('password', None)
        traveller = Traveller.objects.create(**validated_data)
        if password:
            traveller.set_password(password)  # ✅ hashes the password
            traveller.save()
        return traveller
    
class TravellerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveller
        fields = '__all__'