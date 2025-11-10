from django.db import models
from django.conf import settings
import requests
from payments.models import Traveller
from authentication.models import User, Company
from django.contrib.auth import get_user_model
import re

from utils.utils import generate_slug, upload_to_cloudflare


# Create your models here.
class Tour(models.Model):
    # Basic Info
    name = models.CharField(max_length=255, null=True, blank=True )
    description = models.TextField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    published = models.BooleanField(default=True, null=True, blank=True)

    # Additional Info
    duration = models.CharField(max_length=100, null=True, blank=True)
    group_size = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=500, null=True, blank=True)
    tag = models.CharField(max_length=500, null=True, blank=True)
    reviews = models.CharField(max_length=100, null=True, blank=True)
    location_type = models.CharField(max_length=255, null=True, blank=True)
    inclution = models.TextField(null=True, blank=True)
    exclusion = models.TextField(null=True, blank=True)
    cancellation = models.CharField(max_length=500, null=True, blank=True)
    meeting_point = models.CharField(max_length=500, null=True, blank=True)
    map_url = models.CharField(max_length=10000, null=True, blank=True)
    languages = models.CharField(max_length=500, null=True, blank=True)
    additional_info = models.CharField(max_length=5000, null=True, blank=True)
    know_before_you_go = models.TextField(null=True, blank=True)

    # Pricing Info
    price_by_vehicle = models.BooleanField(default=False, null=True, blank=True)
    price_by_passenger = models.BooleanField(default=False, null=True, blank=True)
    is_bokun_url = models.BooleanField(default=True, null=True, blank=True)

    # Image Info
    thumbnail_image = models.ImageField(upload_to='tour/ThumbnailImage/', null=True, blank=True)
    update_thumbnail_image = models.BooleanField(default=False, null=True, blank=True)
    cloudflare_thumbnail_image_url = models.URLField(max_length=500, null=True, blank=True)

    # Metadata
    meta_title = models.CharField(max_length=500, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Tours'
        ordering = ['-id' ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # when we try to update an existing object. process of updating the thumbnail image to the cloudflare
        if self.pk:
            print("entering save method for update")
            #checking wheather we have sent any new thumbnail_image or not
            if self.update_thumbnail_image: 
                print("update_thumbnail_image flag is True, uploading thumbnail image to Cloudflare...")
                # If update_thumbnail_image is True, upload the thumbnail image to Cloudflare
                if self.thumbnail_image:
                    try:
                        print("Uploading thumbnail image to Cloudflare from 'update' part of save method...")
                        self.cloudflare_thumbnail_image_url = upload_to_cloudflare(self.thumbnail_image)
                        print("Cloudflare thumbnail image URL:", self.cloudflare_thumbnail_image_url)
                        self.update_thumbnail_image = False  # Reset the flag after upload
                        print(f"update_thumbnail_image flag reset to {self.update_thumbnail_image}")
                    except Exception as e:
                        print(f"Error uploading thumbnail image to Cloudflare: {str(e)}")
                else:
                    print("No thumbnail image provided for upload.")
            else:
                print("update_thumbnail_image flag is False, skipping Cloudflare upload for thumbnail image.")
                pass

        # when we try to create new object
        else:
            print("entering save method for create")
            if self.thumbnail_image:
                try:
                    print("Uploading thumbnail image to Cloudflare from 'create' part of save method...")
                    self.cloudflare_thumbnail_image_url = upload_to_cloudflare(self.thumbnail_image)
                    print("Cloudflare thumbnail image URL:", self.cloudflare_thumbnail_image_url)
                except Exception as e:
                    print(f"Error uploading thumbnail image to Cloudflare: {str(e)}")
            else :
                print("No thumbnail image provided for upload.")
                pass



        # Generate slug from name
        # if self.name:
        #     # Replace special characters (including underscore) with hyphens
        #     clean_name = generate_slug(self.name)
        #     slug = clean_name
        #     counter = 1

        #     while Tour.objects.filter(slug = slug).exclude(id=self.id).exists():
        #         slug = f"{clean_name}-{counter}"
        #         counter += 1

        #     self.slug = slug

        super().save(*args, **kwargs)



class TourContentImage(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tour_images',null=True, blank=True)
    head = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='tour/ContentImage/',null=True, blank=True, unique=True)
    update_image = models.BooleanField(default=False, null=True, blank=True)
    cloudflare_image_url = models.URLField(max_length=500, null=True, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    

    class Meta:
        verbose_name_plural = 'TourContentImages'
        ordering = ('-id', )

    def __str__(self):
        return f"Image {self.id}"
        
    def save(self, *args, **kwargs):
        skip_cloudflare = getattr(self, "_skip_cloudflare", False)
        print("skip_cloudflare is : ", skip_cloudflare)

        if not skip_cloudflare:  

            if self.pk:
                print("entering save method for update")
                #checking wheather we have sent any new image or not
                if self.update_image: 
                    print("update_image flag is True, uploading image to Cloudflare...")
                    # If update_image is True, upload the image to Cloudflare
                    if self.image:
                        try:
                            print("Uploading image to Cloudflare from 'update' part of save method...")
                            self.cloudflare_image_url = upload_to_cloudflare(self.image)
                            print("Cloudflare image URL:", self.cloudflare_image_url)
                            self.update_image = False  # Reset the flag after upload
                            print(f"update_image flag reset to {self.update_image}")
                        except Exception as e:
                            print(f"Error uploading image to Cloudflare: {str(e)}")
                    else:
                        print("No image provided for upload.")
                else:
                    print("update_image flag is False, skipping Cloudflare upload for image.")
                    pass

            # when we try to create new object
            else:
                print("entering save method for create")
                if self.image:
                    try:
                        print("Uploading image to Cloudflare from 'create' part of save method...")
                        self.cloudflare_image_url = upload_to_cloudflare(self.image)
                        print("Cloudflare image URL:", self.cloudflare_image_url)
                    except Exception as e:
                        print(f"Error uploading image to Cloudflare: {str(e)}")
                else :
                    print("No image provided for upload.")
                    pass

        super().save(*args, **kwargs)
  
class DayTourPrice(models.Model):
    GUIDE_CHOICES = [
        ('With Guide', 'With Guide'),
        ('Without Guide', 'Without Guide'),
    ]
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='day_tour_price_list')
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    group_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    guide = models.CharField(max_length=20, choices=GUIDE_CHOICES, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Day Tour Prices List'
        ordering = ('-id', )

    def __str__(self):
        return f"{self.tour.name} - {self.price_per_person} USD per person - {self.group_price} USD group price - {self.guide} "
    
class AvailableDate(models.Model):
    day_tour_price = models.ForeignKey(DayTourPrice, on_delete=models.CASCADE, related_name='available_dates')
    date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"{self.day_tour_price.tour.name} - {self.date}"

class AvailableTime(models.Model):
    day_tour_price = models.ForeignKey(DayTourPrice, on_delete=models.CASCADE, related_name='available_times')
    time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.day_tour_price.tour.name} - {self.time}"
    
    
class TourBooking(models.Model):
     # Payment status should include refunded and partially refunded for clarity
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partial_refund', 'Partial Refund'),
        ('refunded', 'Refunded'),
        ('unpaid', 'Unpaid'),
        ('cancelled', 'Cancelled'),
        ('cancelled without refund', 'Cancelled Without Refund'),
        ('cancelled by admin', 'Cancelled By Admin'),
        ('failed', 'Failed'),
    ]

    DATE_CHANGE_REQUEST_STATUS_CHOICES = [
        ('reviewing', 'Reviewing'),
        ('cancelled', 'Cancelled'),
        ('approved', 'Approved'),  # if date change request has been approved
        ('denied', 'Denied'), # if date change request has been denied by admin 
    ]

    CANCELLATION_STATUS_CHOICES = [
        ('reviewing', 'Reviewing'),
        ('approved', 'Approved'),  # cancellation request is accepted
        ('denied', 'Denied'), # if cancellation request has been denied by admin
    ]

    booking_id = models.CharField(max_length=20, null=True, blank=True)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="tour_bookings", null=True, blank=True)
    guide = models.CharField(max_length=20, null=True, blank=True)

    traveller = models.ForeignKey(Traveller, on_delete=models.CASCADE, related_name="tour_bookings", null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tour_bookings", null=True, blank=True)

    total_participants = models.PositiveIntegerField(null=True, blank=True)
    
    # Date handling
    previous_selected_date = models.DateField(null=True, blank=True)
    selected_date = models.DateField(null=True, blank=True)
    selected_time = models.TimeField(null=True, blank=True)
    
    # Date change request workflow
    date_change_request = models.BooleanField(default=False)
    requested_selected_date = models.DateField(null=True, blank=True)
    date_request_approved = models.BooleanField(default=False)
    date_change_request_status = models.CharField(
        max_length=50,
        choices = DATE_CHANGE_REQUEST_STATUS_CHOICES,
        null=True, blank=True
    )
    
    # Pricing
    price_by_passenger = models.BooleanField(default=False)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    price_by_vehicle = models.BooleanField(default=False)
    group_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Payment tracking
    status = models.CharField(
        max_length=50,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    payment = models.ForeignKey("payments.Payment", on_delete=models.SET_NULL, related_name="tour_bookings", null=True, blank=True)
    payment_key = models.CharField(max_length=255, null=True, blank=True, db_index=True) # Stripe PaymentIntent ID
    payment_url = models.URLField(max_length=2000, null=True, blank=True)

    # Refund tracking
    refund_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., 50.00 for 50%
    requested_refund_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Amount requested for refund
    refunded_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    refund_id = models.CharField(max_length=255, null=True, blank=True)  # Stripe refund ID
    refund_status = models.CharField(max_length=50,
        choices=PAYMENT_STATUS_CHOICES, null=True, blank=True)  
    refund_reason = models.CharField(max_length=1000, null=True, blank=True)


    # Cancellation workflow
    cancellation_eligible = models.BooleanField(default=True)
    cancellation_request = models.BooleanField(default=False)
    cancellation_reason = models.TextField(null=True, blank=True)
    cancellation_status = models.CharField(
        max_length=50,
        choices = CANCELLATION_STATUS_CHOICES,
        null=True, blank=True
    )
    manually_cancelled_by_admin = models.BooleanField(default=False, null=True, blank=True)
    cancellation_denied_count = models.IntegerField(default=0, null=True, blank=True)  # Track how many times cancellation was denied

    # QR code 
    qr_code = models.ImageField(upload_to="booking_qr/", null=True, blank=True)
    qr_url = models.URLField(max_length=2000, null=True, blank=True)

    # booking_ticket & payment_invoice
    booking_ticket = models.FileField(upload_to='tour_booking_ticket/', null=True, blank=True)
    payment_invoice = models.FileField(upload_to='payment_invoice/', null=True, blank=True)

    # booking uuid 
    booking_uuid = models.CharField(max_length=100, unique=True, null=True, blank=True)

    # Metadata
    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.CharField(max_length=50, null=True, blank=True)
    updated_by = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Tour Bookings'
        ordering = ('-id',)

    def __str__(self):
        traveller_name = self.traveller.user.username if self.traveller else "No Traveller"
        tour_name = self.tour.name if self.tour else "No Tour"

        return f"Booking for {tour_name} by {traveller_name} -  {self.total_price}"
    
class TourItinerary(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name="itineraries_list", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    lat = models.FloatField(max_length=1000, null=True, blank=True)
    long = models.FloatField(max_length=1000, null=True, blank=True)   

    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Itineraries List'
        ordering = ('-id', )

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
   
# ei chart ta ekdom thik range niye update kore dilam:

# > 60 hours before event → Full refund (0% fee)

# 24 to 60 hours before event → 25% fee (75% refund)

# 0 to 24 hours before event → 50% fee (50% refund)


class PenaltyRules(models.Model):
    cancellation_policy_list = models.ForeignKey('tour.CancellationPolicy',on_delete=models.CASCADE,related_name="penalty_rules")
    days_before = models.IntegerField(null=True, blank=True)  # e.g., 0, 1, 2
    hours_before = models.IntegerField(null=True, blank=True)  # e.g., 0, 24, 48
    cutoff_hours = models.IntegerField(null=True, blank=True)  # e.g., 24, 48, 72
    charge_type = models.CharField(max_length=50, null=True, blank=True)  # percentage, fixed
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # e.g., 50.00

    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Penalty Rules'
        ordering = ('cutoff_hours',)

    def __str__(self):
        return f"{self.percentage}% charge if cancelled within {self.cutoff_hours} hours"
   
class CancellationPolicy(models.Model):
    POLICY_TYPE_CHOICES = [
        ('simple', 'SIMPLE'),
        ('advanced', 'ADVANCED'),
        ('full_refund', 'FULL_REFUND'),
        ('non_refundable', 'NON_REFUNDABLE'),
    ]

    tour = models.ForeignKey("tour.Tour",on_delete=models.CASCADE,related_name="cancellation_policies_list")
    title = models.CharField(max_length=255, null=True, blank=True)
    default_policy = models.BooleanField(default=False, null=True, blank=True)
    policy_type = models.CharField(max_length=50,choices=POLICY_TYPE_CHOICES,null=True,blank=True)
    simple_cutoff_hours = models.IntegerField(null=True, blank=True, default=0)

    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Cancellation Policies'
        ordering = ('id',)

    def __str__(self):
        return f"{self.title or 'Unnamed Policy'} ({self.policy_type})"
    
class OldAgentBooking(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('unpaid','Unpaid')
    ]
    old_id = models.IntegerField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete= models.CASCADE)

    invoice_no = models.CharField(max_length=255, null=True, blank=True)
    agent = models.TextField(null=True, blank=True)
    tour = models.CharField(max_length=255, null=True, blank=True)
    traveller = models.TextField(null=True, blank=True)

    adult_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)  
    youth_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    child_price = models.DecimalField(default=0, max_digits=20, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost  = models.DecimalField(default=0, max_digits=10, decimal_places=2, null=True, blank=True)

    coupon_text = models.CharField(max_length=255, null=True, blank=True)
    is_coupon_applied = models.BooleanField(default=False, null=True, blank=True)
    applied_coupon_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage', null=True, blank=True)
    coupon_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coupon_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    coupon_applied_final_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_type = models.CharField(max_length=20, choices=(('percentage', 'Percentage'), ('value', 'Value')), default='percentage', null=True, blank=True)
    is_cancelled = models.BooleanField(default=False,null=True, blank=True)
    participants = models.JSONField(null=True, blank=True)
    selected_date = models.DateField(null=True, blank=True)
    selected_time = models.TimeField(null=True, blank=True)
    payWithCash = models.BooleanField(default=False, null=True, blank=True)
    payWithStripe = models.BooleanField(default=False, null=True, blank=True)
    duration = models.CharField(max_length=50,null=True, blank=True)
    is_agent = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, null=True, blank=True)
    payment = models.TextField(null=True, blank=True)
    payment_key = models.CharField(max_length=1000, null=True, blank=True)
    email_pdf = models.CharField(max_length=1000, null=True, blank=True)
    booking_invoice_pdf = models.CharField(max_length=1000, null=True, blank=True)
    url = models.CharField(max_length=10000, null=True, blank=True)

    # created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    # updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'OldAgentBooking'
        ordering = ('-id',)

    def __str__(self):
        # return f"Booking for {self.tour} by {self.agent} -  {self.total_price}"        
        return f"data from invoice number : {self.invoice_no}"