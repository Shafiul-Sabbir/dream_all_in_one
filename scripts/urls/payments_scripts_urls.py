from django.urls import path
from scripts.views import payments_scripts_views as views


urlpatterns = [
    # 1
    path('api/v1/load_payment/<int:company_id>/', views.load_Payment), 

    path('api/v1/load_traveller/<int:company_id>/', views.load_Traveller), 

]