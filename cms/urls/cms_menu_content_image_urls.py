from django.urls import path

from cms.views import cms_menu_content_image_views as views


urlpatterns = [

	path('api/v1/cms_menu_content_image/all/', views.getAllCMSMenuContentImage),

	path('api/v1/cms_menu_content_image/without_pagination/all/', views.getAllContentImageWP),

	path('api/v1/get_all_cms_menu_content_image_by_cms_menu_id/<int:menu_id>/', views.getAllContentImageByMenuId),
    
	# have to optimize it , present response time is 1ms for 0 queries
	path('api/v1/get_all_cms_menu_content_image_list_by_cms_menu_id/<int:menu_id>/', views.getAllContentImageListByMenuId),
	# There is nothing to change to notice a significant performance improvement. it has used direct sql query, 
	# not any django ORM. so it is now in its optimal state.

	path('api/v1/cms_menu_content_image/<str:image_name>/', views.getACMSMenuContentImageByContentTitle), #actually we will pass the 'head' of the content for finding the full content

	path('api/v1/cms_menu_content_image/create/', views.createCMSMenuContentImage),

	path('api/v1/cms_menu_content_image/update/<int:pk>', views.updateCMSMenuContentImage),

	path('api/v1/cms_menu_content_image/delete/<int:pk>', views.deleteCMSMenuContentImage),
    
	path('api/v1/get_all_cms_menu_content_image_list_by_menu_name/<str:menu_name>/', views.getContentImageListByMenuName),
    
	path('api/v1/get_content_and_images_by_menu_id/<int:menu_id>/', views.getContentAndImagesByMenuId, name='get_content_and_images_by_menu_id'),

]