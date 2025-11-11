from django.db import models
from django.conf import settings

from authentication.models import User, Company
class Traveller(models.Model):
    old_id = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete= models.CASCADE)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='traveller_profile')
    phone = models.CharField(max_length=50, blank=True, null=True)
    accept_offers = models.BooleanField(default=False)

    created_by = models.CharField(max_length=255, blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)

    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} "

    class Meta:
        verbose_name_plural = 'Travellers'
        ordering = ('-created_at', )


class Payment(models.Model):
    old_id = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete= models.CASCADE)

    invoice_id = models.CharField(max_length=255, null=True, blank=True)
    tour_booking = models.ForeignKey("tour.TourBooking", on_delete=models.SET_NULL, related_name="tour_booking", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    traveller = models.ForeignKey(Traveller, on_delete=models.SET_NULL, related_name='payments', null=True, blank=True)
    tour = models.ForeignKey("tour.Tour", on_delete=models.SET_NULL, null=True, blank=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    payWithCash = models.BooleanField(null=True, blank=True,default=False)
    payWithStripe = models.BooleanField(null=True, blank=True,default=False)
    payment_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    payment_url = models.URLField(max_length=2000,null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)



    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    def __str__(self):
        return f"Payment of {self.total_price} USD, Status: {self.payment_status} - created by : {self.created_by or 'Unknown User'}"
