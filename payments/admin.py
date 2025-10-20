from django.contrib import admin
from payments.models import Traveller, Payment
# Register your models here.

@admin.register(Traveller)
class TravellerAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Traveller._meta.fields]
	#  Traveller._meta : Eta ekta ModelOptions object, ja model-er sob internal info store kore.
	# fields: Eta model-er sob field-er list return kore.
	readonly_fields = ('created_at', 'updated_at')
	
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in Payment._meta.fields]
	readonly_fields = ('created_at', 'updated_at')