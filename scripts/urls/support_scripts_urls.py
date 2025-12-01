from django.urls import path
from scripts.views import support_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_LoggedUser/<int:company_id>/', views.load_LoggedUser), #load general settings for a company
]