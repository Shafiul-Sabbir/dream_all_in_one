from django.urls import path
from payments.views import stripe_webhook as views
urlpatterns = [
    path('api/v1/payments/stripe-webhook/', views.stripe_webhook),

    # by entering booking id admin can refund balance from stripe to traveller account
    path('api/v1/payments/refund_balance_from_stripe_to_traveller/<int:pk>/', views.refundBalanceFromStripeToTraveller)
]
