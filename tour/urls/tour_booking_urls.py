from django.urls import path

from tour.views import tour_booking_views as views

urlpatterns = [
    path('api/v1/tour_booking/create/', views.createTourBooking),
        
	path('api/v1/tour_booking/all/', views.getAllTourBooking),
    # path('api/v1/tour_booking_list_by_agent/all/<str:agent_ref_no>/', views.tour_booking_list_by_agent),
    
	# path('api/v1/tour_booking/booked_data/', views.getAllBookedTourBooking),
 
    path('api/v1/tour_booking/all/without_pagination/', views.getAllTourBookingWithoutPagination),

	path('api/v1/tour_booking/<int:pk>/', views.getATourBooking),
    
	path('api/v1/tour_booking/get_a_booking_by_booking_uuid/<str:booking_uuid>/', views.getATourBookingByBookingUUID),
    
	path('api/v1/tour_booking/get_a_booking_by_booking_id/<str:booking_id>/', views.getATourBookingByBookingID),
    
	path('api/v1/tour_booking/get_all_tour_booking_by_traveller_id/<int:pk>/', views.getAllTourBookingByTravellerID),
    
	path('api/v1/tour_booking/get_all_tour_booking_by_given_keyword/', views.getAllTourBookingByGivenKeyword),

	path('api/v1/tour_booking/update/<int:pk>/', views.updateTourBooking),
	
	path('api/v1/tour_booking/delete/<int:pk>/', views.deleteTourBooking),
    
	# path('api/v1/tour_booking/agent_booking_details/', views.getAgentBookingDetails),
    
	path('api/v1/tour_booking/date/update/', views.requestToUpdateATourBookingDate),
    
	path('api/v1/tour_booking/approve_date_change_request/<int:pk>/', views.approveDateChangeRequest),
    
	path('api/v1/tour_booking/deny_date_change_request/<int:pk>/', views.denyDateChangeRequest),
    
	path('api/v1/tour_booking/checking_cancellation_policies/<int:pk>/', views.requestToCheckCancellationPolicies),

	path('api/v1/tour_booking/cancel_request/<int:pk>/', views.requestToCancelTourBooking),
    
	# if admin wants to approve a cancellation request he will use this endpoint
    # by entering booking id admin can refund balance from stripe to traveller account
    path('api/v1/tour_booking/approve_booking_cancellation_request_and_refund_balance_from_stripe_to_traveller/<int:pk>/', views.approveBookingCancellationRequest),

    path('api/v1/tour_booking/deny_cancellation_request/<int:pk>/', views.denyCancellationRequest),
    
	path('api/v1/tour_booking/manual_cancellation_of_booking_by_admin/<int:pk>/', views.ManualCancellationOfBookingByAdmin),

] 
