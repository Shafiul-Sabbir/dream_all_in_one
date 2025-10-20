from django.urls import path
from tour.views import tour_content_views as views

urlpatterns = [
    path('api/v1/tour/all/', views.getAllTour),
    path('api/v1/tour/<int:pk>/', views.getATour),
    path('api/v1/tour/create/', views.createTour),
    path('api/v1/tour/update/<int:pk>/', views.updateTour),
    path('api/v1/tour/delete/<int:pk>/', views.deleteTour),
    # path('api/v1/tour/get_by_name/<str:name>/', views.getTourByName),
    # path('api/v1/tour/get_by_date/<str:date>/', views.getTourByDate),
    # path('api/v1/tour/get_by_location/<str:location>/', views.getTourByLocation),
    # path('api/v1/tour/get_by_status/<str:status>/', views.getTourByStatus),
    # path('api/v1/tour/get_by_organizer/<str:organizer>/', views.getTourByOrganizer),
    # path('api/v1/tour/get_by_participant/<str:participant>/', views.getTourByParticipant),
    # path('api/v1/tour/get_by_tour_type/<str:tour_type>/', views.getTourByTourType),
    # path('api/v1/tour/get_by_tour_date_range/<str:start_date>/<str:end_date>/', views.getTourByDateRange),
    # path('api/v1/tour/get_by_tour_status/<str:status>/', views.getTourByStatus),
    # path('api/v1/tour/get_by_tour_organizer/<str:organizer>/', views.getTourByOrganizer),
]