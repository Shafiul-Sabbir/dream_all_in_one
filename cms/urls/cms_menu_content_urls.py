from django.urls import path
from cms.views import cms_menu_content_views as views


urlpatterns = [
    
	# have to optimize it , present response time is 107ms and 43 queries
	path('api/v1/cms_menu_content/all/', views.getAllCMSMenuContent),
    # after using select_related and prefetch_related it becomes 40ms and 14 queries

	path('api/v1/cms_menu_content/without_pagination/all/', views.getAllCMSMenuContentWithoutPagination),

	path('api/v1/get_all_cms_menu_content_by_cms_menu_id/<int:menu_id>/', views.getAllCMSMenuContentByCMSMenuId),

	path('api/v1/cms_menu_content/<int:pk>/', views.getACMSMenuContent),

	# have to optimize it , present response time is 14ms for 2 queries
	path('api/v1/cms_menu_content/get_cms_menu_content_by_cms_menu_id/<int:pk>/', views.getCMSMenuContentByCMSMenuID),
	# after using select_related it becomes 20ms for 2 queries. but optimization will be noticed for large datasets

    
	path('api/v1/cms_menu_content/get_cms_menu_content_by_cms_menu_name/<str:menu_name>/', views.getCMSMenuContentByCMSMenuName),
    
    # path('api/v1/cms_menu_content/<str:menu_name>/<str:content_name>/', views.get_menu_content_by_name),
    
	path('api/v1/get_cms_menu_content_by_slug/<str:slug>/', views.get_menu_content_by_slug),
    
	path('api/v1/cms_menu_content/create/', views.createCMSMenuContent),

	path('api/v1/cms_menu_content/update/<int:pk>/', views.updateCMSMenuContent),
	
	path('api/v1/cms_menu_content/delete/<int:pk>/', views.deleteCMSMenuContent),

]