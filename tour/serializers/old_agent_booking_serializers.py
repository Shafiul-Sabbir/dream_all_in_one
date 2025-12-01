from requests import Response
from rest_framework import serializers
from tour.models import OldAgentBooking

class OldAgentBookingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = OldAgentBooking
        fields = '__all__'
