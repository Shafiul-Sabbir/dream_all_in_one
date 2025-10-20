from django.urls import path
from tour.views import tour_itinerary_views as views
urlpatterns = [
    # path('api/v1/Itinerary/create/', views.createItinerary),

	path('api/v1/Itinerary/update/<int:pk>/', views.updateItinerary),
	
	path('api/v1/Itinerary/delete/<int:pk>/', views.deleteItinerary),

    path('api/v1/get_itinerary_by_itinerary_id/<int:pk>/', views.getAItinerary),

	path('api/v1/Itinerary/all/', views.getAllItinerary),

	path('api/v1/Itinerary/without_pagination/all/', views.getAllItineraryWithoutPagination),

	path('api/v1/get_all_Itinerary_by_tour_id/<int:tour_id>/', views.getAllItineraryByTourId),
    
	path('api/v1/populate_tour_with_menu_itineraries/', views.populateToursWithMenuItineraries),


]