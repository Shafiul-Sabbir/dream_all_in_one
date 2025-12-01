from django.contrib import admin
from .models import TourItinerary, TourBooking, Tour, DayTourPrice, AvailableDate, AvailableTime, TourContentImage, CancellationPolicy, PenaltyRules, OldAgentBooking
# Register your models here.

@admin.register(Tour)
class tourAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Tour._meta.fields]
	
@admin.register(DayTourPrice)
class DayTourPriceAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DayTourPrice._meta.fields]
    list_filter = ('tour', 'guide')

@admin.register(AvailableDate)
class AvailableDateAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AvailableDate._meta.fields]
    list_filter = ('day_tour_price',)

@admin.register(AvailableTime)
class AvailableTimeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in AvailableTime._meta.fields]
    list_filter = ('day_tour_price',)
    
@admin.register(TourBooking)
class TempTourBookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourBooking._meta.fields]

@admin.register(TourContentImage)
class TourContentImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourContentImage._meta.fields]
    list_filter = ('tour',)
    search_fields = ('tour__name', 'head')  # Assuming 'name' is a field in the Tour model

@admin.register(TourItinerary)
class TourItineraryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TourItinerary._meta.fields]
    list_filter = ('tour',)
    search_fields = ('tour__name', 'title')

@admin.register(CancellationPolicy)
class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CancellationPolicy._meta.fields]
    list_filter = ('tour',)
    search_fields = ('tour__name', 'cancellation')

@admin.register(PenaltyRules)
class PenaltyRulesAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PenaltyRules._meta.fields]
    list_filter = ('cancellation_policy_list',)

@admin.register(OldAgentBooking)
class OldAgentBookingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OldAgentBooking._meta.fields]
    
    