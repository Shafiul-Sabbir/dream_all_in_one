from django.urls import path, include
from payments.views import agent_views as views
urlpatterns = [
    path('api/v1/agent/create/', views.createAgent),
        
    path('api/v1/agent/simple_agent_creation/', views.simpleAgentCreation),

    path('api/v1/agent/update/<int:pk>/', views.updateAgent),

    path('api/v1/agent/<int:pk>/', views.getAnAgent),

    path('api/v1/agent/all/', views.getAllAgent),

    path('api/v1/agent/delete/<int:pk>/', views.deleteAgent),

]