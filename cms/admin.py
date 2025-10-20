from django.contrib import admin

from cms.models import *



# Register your models here.

@admin.register(CMSMenu)
class CMSMenuAdmin(admin.ModelAdmin):
	list_display = [field.name for field in CMSMenu._meta.fields]


@admin.register(CMSMenuContent)
class CMSMenuContentAdmin(admin.ModelAdmin):
	list_display = [field.name for field in CMSMenuContent._meta.fields]



@admin.register(CMSMenuContentImage)
class CMSMenuContentImageAdmin(admin.ModelAdmin):
	list_display = [field.name for field in CMSMenuContentImage._meta.fields]

### adding email address




@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
	list_display = [field.name for field in EmailAddress._meta.fields]


@admin.register(SendEmail)
class SendEmailAdmin(admin.ModelAdmin):

	list_display = [field.name for field in SendEmail._meta.fields]




@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):

	list_display = [field.name for field in Itinerary._meta.fields]

