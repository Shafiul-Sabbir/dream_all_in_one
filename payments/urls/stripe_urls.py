from django.urls import path
from payments.views import stripe_webhook as views
urlpatterns = [
    path('api/v1/payments/stripe-webhook/', views.stripe_webhook),

]
