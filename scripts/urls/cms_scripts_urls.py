from django.urls import path
from scripts.views import cms_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_CMSMenu/<int:company_id>/', views.load_CMSMenu), #load cms menu for a company

    path('api/v1/handle_CMSMenu_parent/<int:company_id>/', views.handle_CMSMenu_parent), #handle cms menu parent for a company

    # 2
    path('api/v1/load_CMSMenuConent/<int:company_id>/', views.load_CMSMenuContent), #load cms menu content for a company

    # 3
    path('api/v1/load_CMSMenuContentImage/<int:company_id>/', views.load_CMSMenuContentImage), #handle cms menu content image for a company

    # 4
    path('api/v1/load_BlogCategory/<int:company_id>/', views.load_BlogCategory), #load Blog Category for a company
    path('api/v1/handle_BlogCategory_created_at/<int:company_id>/', views.handle_BlogCategory_created_at),
    
    # 5
    path('api/v1/load_Blog/<int:company_id>/', views.load_Blog), #load Blog Category for a company

]