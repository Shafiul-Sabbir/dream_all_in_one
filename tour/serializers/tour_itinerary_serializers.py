from rest_framework import serializers
from tour.models import TourItinerary
class TourItinerarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourItinerary
        fields = '__all__'  

class TourItineraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourItinerary
        fields = '__all__'