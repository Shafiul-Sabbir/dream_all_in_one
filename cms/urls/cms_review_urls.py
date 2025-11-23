
from django.urls import path

from cms.views import cms_review_views as views


urlpatterns = [
	# have to optimize it, response time is 40ms and 3 queries.
	path('api/v1/cms_review/all/', views.getAllReview),
	# after using pagination present response time is 10ms and 4 queries.
    
	path('api/v1/cms_review/without_pagination/all/', views.getAllReviewWithoutPagination),
    
	path('api/v1/cms_review/create/', views.createReview),

	path('api/v1/cms_review/update/<int:pk>/', views.updateReview),

	path('api/v1/cms_review/delete/<int:pk>/', views.deleteReview),


    

]