from django.urls import path
from scripts.views import authentication_scripts_views as views


urlpatterns = [
	path('api/v1/load_users/<int:company_id>', views.load_users), #load users for a company

    path('api/v1/load_roles/<int:company_id>', views.load_roles), #load roles for a company

    path('api/v1/load_permissions/<int:company_id>', views.load_permissions), #load permissions for a company

    path('api/v1/load_countries/<int:company_id>', views.load_countries), #load countries for a company
]