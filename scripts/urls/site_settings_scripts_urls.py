from django.urls import path
from scripts.views import site_settings_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_GeneralSetting/<int:company_id>/', views.load_GeneralSetting), #load general settings for a company

    # 2
    path('api/v1/load_HomePageSlider/<int:company_id>/', views.load_HomePageSlider), #save general settings for a company
]