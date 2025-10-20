from django.urls import path

from tour.views import tour_cancellation_views as views

urlpatterns = [
    path('api/v1/tour_cancellation_policy/create/', views.createTourCancellationPolicy),

    path('api/v1/get_all_policies_by_tour_id/<int:tour_id>/', views.getAllTourCancellationPoliciesByTourId),

    path('api/v1/get_a_policy_by_policy_id/<int:policy_id>/', views.getATourCancellationPolicyByPolicyId),

    # path('api/v1/tour_cancellation_policy/<int:policy_id>/update/', views.updateTourCancellationPolicyByPolicyId),

    path('api/v1/tour_cancellation_policy/<int:policy_id>/delete/', views.deleteTourCancellationPolicyByPolicyId),
]