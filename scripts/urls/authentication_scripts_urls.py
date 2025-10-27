from django.urls import path
from scripts.views import authentication_scripts_views as views


urlpatterns = [
	path('api/v1/load_users/<int:company_id>/', views.load_users), #load users for a company

    path('api/v1/handle_user_metadata/<int:company_id>/', views.handle_user_metadata), #handle user metadata for a company

    path('api/v1/load_roles/<int:company_id>/', views.load_roles), #load roles for a company

    path('api/v1/handle_role_metadata/<int:company_id>/', views.handle_role_metadata), #handle role metadata for a company

    path('api/v1/load_permissions/<int:company_id>/', views.load_permissions), #load permissions for a company

    path('api/v1/handle_permission_metadata/<int:company_id>/', views.handle_permission_metadata), #handle permission metadata for a company

    path('api/v1/load_countries/<int:company_id>/', views.load_countries), #load countries for a company

    path('api/v1/handle_country_metadata/<int:company_id>/', views.handle_country_metadata), #handle country metadata for a company
]