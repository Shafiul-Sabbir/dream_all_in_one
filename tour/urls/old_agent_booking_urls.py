from django.urls import path

from tour.views import old_agent_booking_views as views

urlpatterns = [
    path('api/v1/old_agent_booking/all/', views.getAllOldAgentBooking),

	path('api/v1/old_agent_booking/<int:pk>/', views.getAnOldAgentBooking),

	# path('api/v1/tour_booking/<str:booking_uuid>/', views.getATourBookingByBookingUUID),

	path('api/v1/old_agent_booking/get_all_old_agent_booking_by_company_id/', views.getAllOldAgentBookingByCompanyID),

    path('api/v1/old_agent_booking/get_all_old_agent_booking_by_company_id_with_pagination/', views.getAllOldAgentBookingByCompanyIDWithPagination),


]