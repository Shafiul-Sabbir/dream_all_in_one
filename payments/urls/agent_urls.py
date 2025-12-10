from django.urls import path, include
from payments.views import agent_views as views
urlpatterns = [
    path('api/v1/agents/create/', views.createAgent),
        
    path('api/v1/simple_agent_creation/create/', views.simpleAgentCreation),
]