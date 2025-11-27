from django.urls import path, include
from payments.views import payments_views as views
urlpatterns = [
    path('api/v1/payments/checkout/create/', views.createCheckout),
    # path('api/v1/payments/all/', views.getAllPayments),
    # path('api/v1/payments/<int:pk>/', views.getAPayment),
    # path('api/v1/payments/create/', views.createPayment),
    # path('api/v1/payments/update/<int:pk>/', views.updatePayment),
    # path('api/v1/payments/delete/<int:pk>/', views.deletePayment),
    path('api/v1/payments/availability/check/', views.checkAvailability),

    path('api/v1/resend_email/', views.resendEmail),

]