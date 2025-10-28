from django.urls import path
from scripts.views import cms_scripts_views as views


urlpatterns = [
    #1
    path('api/v1/load_CMSMenu/<int:company_id>/', views.load_CMSMenu), #load cms menu for a company

    path('api/v1/handle_CMSMenu_parent/<int:company_id>/', views.handle_CMSMenu_parent), #handle cms menu metadata for a company

    #2
    path('api/v1/load_CMSMenuConent/<int:company_id>/', views.load_CMSMenuContent), #load cms menu for a company

    # path('api/v1/handle_CMSMenu_parent/<int:company_id>/', views.handle_CMSMenu_parent), #handle cms menu metadata for a company

]