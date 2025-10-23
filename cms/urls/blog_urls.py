
from django.urls import path

from cms.views import cms_blog_views as views


urlpatterns = [
	# have to optimize it, response time is 140ms and 63 queries.
	path('api/v1/cms_blog/all/', views.getAllBlog),
    # after using select_related present response time is 70ms and 23 queries.

	path('api/v1/cms_blog/without_pagination/all/', views.getAllBlogWithoutPagination),
    
	path('api/v1/cms_blog/image_upload/', views.uploadImage),

    path('api/v1/cms_blog/search/', views.searchBlog),

	path('api/v1/cms_blog/<int:pk>', views.getBlog),

	path('api/v1/cms_blog/create/', views.createBlog),

	path('api/v1/cms_blog/update/<int:pk>', views.updateBlog),
	
	path('api/v1/cms_blog/delete/<int:pk>', views.deleteBlog),
    
	path('api/v1/cms_blog/get_blogBy_blog_title_slug/<slug>', views.getBlogByTitle),


]