from django.urls import path
from scripts.views import tour_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_old_agent_bookings/<int:company_id>/', views.load_old_agent_bookings), #load general settings for a company

    path('api/v1/load_tour/<int:company_id>/', views.load_Tour), 

    path('api/v1/load_tour_content_image/<int:company_id>/', views.load_TourContentImage), 

    path('api/v1/load_day_tour_price/<int:company_id>/', views.load_DayTourPrice), 

    path('api/v1/load_available_date/<int:company_id>/', views.load_AvailableDate), 

    path('api/v1/load_available_time/<int:company_id>/', views.load_AvailableTime), 

    path('api/v1/load_tour_itinerary/<int:company_id>/', views.load_TourItinerary), 

    path('api/v1/load_cancellation_policy/<int:company_id>/', views.load_CancellationPolicy), 

    path('api/v1/load_penalty_rules/<int:company_id>/', views.load_PenaltyRules), 

    path('api/v1/load_tour_booking/<int:company_id>/', views.load_TourBooking), 

    path('api/v1/handle_payment_field_for_tour_booking/<int:company_id>/', views.handle_payment_field_for_TourBooking), 









]