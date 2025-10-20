from payments.models import Payment
from rest_framework import serializers

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def create(self, validated_data):
        payment = Payment.objects.create(**validated_data)
        payment.save()

        return payment