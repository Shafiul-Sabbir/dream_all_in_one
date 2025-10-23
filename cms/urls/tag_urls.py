
from django.urls import path
from cms.views import tag_views as views


urlpatterns = [
	path('api/v1/tag/all/', views.getAllTag),

	path('api/v1/tag/without_pagination/all/', views.getAllTagWithoutPagination),

	path('api/v1/tag/<int:pk>', views.getATag),

	path('api/v1/tag/search/', views.searchTag),

	path('api/v1/tag/create/', views.createTag),

	path('api/v1/tag/update/<int:pk>', views.updateTag),

	path('api/v1/tag/delete/<int:pk>', views.deleteTag),



]