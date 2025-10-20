from django.urls import path

from tour.views import tour_content_image_views as views


urlpatterns = [

	path('api/v1/tour_content_image/create/', views.createTourContentImage),

	path('api/v1/tour_content_image/all/', views.getAllTourContentImage),

	path('api/v1/tour_content_image/without_pagination/all/', views.getAllContentImageWP),

	path('api/v1/get_all_tour_content_image_by_tour_id/<int:tour_id>', views.getAllContentImageByTourId),

	path('api/v1/get_all_tour_content_image_list_by_tour_id/<int:tour_id>', views.getAllContentImageListByTourId),

	path('api/v1/tour_content_image/<str:image_head>', views.getATourContentImageByImageHead),

	path('api/v1/tour_content_image/update/<int:pk>', views.updateTourContentImage),

	path('api/v1/tour_content_image/delete/<int:pk>', views.deleteTourContentImage),
    
	path('api/v1/get_all_tour_content_image_list_by_tour_name/<str:tour_name>', views.getContentImageListByTourName),
    
	path('api/v1/get_content_and_images_by_tour_id/<int:tour_id>/', views.getContentAndImagesByTourId, name='get_content_and_images_by_menu_id'),
    
	path('api/v1/populate_tours_with_menuContentIimages/', views.populateToursWithMenuContentImages),

]