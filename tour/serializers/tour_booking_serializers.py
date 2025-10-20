
import datetime
from datetime import datetime
from django.conf import settings
from requests import Response
from rest_framework import serializers
from tour.models import TourBooking, Tour

class TourBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourBooking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def update(self, instance, validated_data):
    #     # check if payload ONLY contains date_change_request and selected_date
    #     if (
    #         set(validated_data.keys()) == {"date_change_request", "selected_date"} 
    #         and validated_data.get("date_change_request") is False
    #     ):
    #         print("from if part of update method of TourBookingSerializer")
    #         # Special case: Admin approval
    #         instance.previous_selected_date = instance.selected_date
    #         instance.selected_date = validated_data.get("selected_date")
    #         instance.date_change_request = False
    #         instance.date_change_request_status = 'approved'
    #         instance.requested_selected_date = None
    #         instance.date_request_approved = True
    #     else:
    #         print("from else part of update method of TourBookingSerializer")
    #         # Normal update (no date_change_request field expected here)
    #         if "date_change_request" in validated_data:
    #             validated_data.pop("date_change_request")  # ensure not allowed here
    #         instance = super().update(instance, validated_data)

        # always update updated_at
        instance.updated_at = datetime.now()
        instance.save()
        return instance
    
class TourBookingListSerializer(serializers.ModelSerializer):
    tour = serializers.StringRelatedField()

    class Meta:
        model = TourBooking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tour_id'] = instance.tour.id if instance.tour else None
        representation['tour'] = instance.tour.name if instance.tour else None
        representation['cloudflare_thumbnail_image_url'] = instance.tour.cloudflare_thumbnail_image_url if instance.tour else None
        return representation
    

