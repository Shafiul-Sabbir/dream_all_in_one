from rest_framework import serializers
from tour.models import TourItinerary
class TourItinerarySerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = TourItinerary
        fields = '__all__'  
        
    def create(self, validated_data):
        company = self.context.get('company')
        validated_data['company'] = company
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        company = self.context.get('company')
        validated_data['company'] = company
        return super().update(instance, validated_data)

class TourItineraryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourItinerary
        fields = '__all__'