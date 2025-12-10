from rest_framework import serializers
from payments.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'

    def create(self, validated_data):
        return Agent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


    
class AgentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = '__all__'