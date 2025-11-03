from django.urls import path
from scripts.views import tour_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_old_agent_bookings/<int:company_id>/', views.load_old_agent_bookings), #load general settings for a company
]