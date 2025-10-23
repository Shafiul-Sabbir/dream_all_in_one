
from django.urls import path
from cms.views import blog_category_views as views


urlpatterns = [
	path('api/v1/blog_category/all/', views.getAllBlogCategory),

	# have to optimize it, response time is 3ms and 1 queries.
	path('api/v1/blog_category/without_pagination/all/', views.getAllBlogCategoryWithoutPagination),
	# There is nothing to change to notice a significant performance improvement.    
    
	path('api/v1/blog_category/<int:pk>', views.getABlogCategory),

	path('api/v1/blog_category/search/', views.searchBlogCategory),

	path('api/v1/blog_category/create/', views.createBlogCategory),

	path('api/v1/blog_category/update/<int:pk>', views.updateBlogCategory),

	path('api/v1/blog_category/delete/<int:pk>', views.deleteBlogCategory),



]