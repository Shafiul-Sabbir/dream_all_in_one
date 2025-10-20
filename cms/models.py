import imp
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
import requests


# Create your models here.

class CMSMenu(models.Model):
    parent = models.ForeignKey('self', on_delete=models.PROTECT, related_name='children', null=True, blank=True)
    name = models.CharField(max_length=255)
    position = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenus'
        ordering = ('position', )

    def __str__(self):
        return self.name
	
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class CMSMenuContent(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_contents')
    name = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.CharField(max_length=100,null=True, blank=True)
    inclution = models.TextField(null=True, blank=True)
    exclusion = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=1000, null=True, blank=True)
    price = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'CMSMenuContents'
        ordering = ('order', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)



class CMSMenuContentImage(models.Model):
    cms_menu = models.ForeignKey(CMSMenu, on_delete=models.PROTECT, related_name='cms_menu_content_images')
    head = models.CharField(max_length=500)
    image = models.ImageField(upload_to='cms/ContentImage/',null=True, blank=True)
    cloudflare_image = models.URLField(max_length=500, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    

    class Meta:
        verbose_name_plural = 'CMSMenuContentImages'
        ordering = ('-id', )

    def __str__(self):
        return self.head
        
    def save(self, *args, **kwargs):
        if self.image:
            try:
                self.cloudflare_image = self.upload_cloudflare()
                print("Cloudflare image URL:", self.cloudflare_image)
            except Exception as e:
                print(f"Error uploading image to Cloudflare: {str(e)}")
        super().save(*args, **kwargs)
        
    def upload_cloudflare(self):
        endpoint = 'https://api.cloudflare.com/client/v4/accounts/f8b413899d5239382d13a2665326b04e/images/v1'
        headers = {
            'Authorization': 'Bearer Ook1HC9KydDm4YfqkmVH5KnoNsSugDDqgLFj4QHi',
        }
        files = {
            'file': self.image.file
        }
        response = requests.post(endpoint, headers=headers, files=files)
        response.raise_for_status()
        json_data = response.json()
        variants = json_data.get('result', {}).get('variants', [])
        if variants:
            cloudflare_image = variants[0]  # Use the first variant URL
            print("Cloudflare image URL from response:", cloudflare_image)
            return cloudflare_image
        else:
            print("No variants found in the Cloudflare response")
            return None





 
#add this
class Itinerary(models.Model):
    cms_content = models.ForeignKey(CMSMenuContent, on_delete=models.PROTECT,null=True,blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=1000, null=True, blank=True)
    lat = models.FloatField(max_length=1000, null=True, blank=True)
    lng = models.FloatField(max_length=1000, null=True, blank=True)     
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.SET_NULL, related_name="+", null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Itinerary'
        ordering = ('id', )

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)      


#For Contact



class EmailAddress(models.Model):
    full_name = models.CharField(max_length=255,null=True, blank=True)
    email = models.EmailField(null=False, blank=False)
    subject = models.CharField(max_length=255,null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Email addresses'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
# @receiver(post_save, sender=EmailAddress)
# def send_email_on_new_signup(sender, instance, created, **kwargs):
#     if created:
#         # Send contact confirmation email
#         subject = 'New Customer Contact With us'
#         message = f'Customer Details,\n\n'
#         message += f'Full Name: {instance.full_name}\n'
#         message += f'Email: {instance.email}\n'
#         message += f'Subject: {instance.subject}\n'
#         message += f'Message: {instance.message}\n'
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = ['sales@dreamziarah.com',]
#         # send_mail(subject, message, from_email, recipient_list)

#         # Send feedback email to the sender
#         feedback_subject = 'Your Journey Awaits with Dream Ziarah'
#         feedback_message = 'Dear Customer \n\n'
#         feedback_message += 'Thank you for reaching out to Dream Ziarah! Your inquiry is\nimportant to us, and our dedicated team is already at work to\nprovide you with the information you need. Expect a prompt\nresponse that will help you take the next steps toward your dream\ngetaway.\n\n'
#         feedback_message += 'In the meantime, feel free to explore our website and discover the\nincredible destinations and experiences we offer. We are here to \nmake your travel dreams a reality.\n\n'
#         feedback_message += 'Best regards,\n\n'
#         feedback_message += 'Dream Ziarah\n'
#         feedback_message += 'Customer Support Team\n'
#         feedback_from_email = settings.EMAIL_HOST_USER
#         feedback_recipient_list = [instance.email]
#         # send_mail(feedback_subject, feedback_message, feedback_from_email, feedback_recipient_list)









#For Subscription

class SendEmail(models.Model):
   
    email = models.EmailField(null=False, blank=False)
    class Meta:
        verbose_name_plural = 'Send Email'
        ordering = ('-id', )

    def __str__(self):
        return self.email
    
# @receiver(post_save, sender=SendEmail)
# def send_email(sender, instance, created, **kwargs):
#     if created:
#         # Send subscription confirmation email
#         subject = 'New Email Subscription'
#         message = f'Email: {instance.email}\n'
#         from_email = settings.EMAIL_HOST_USER
#         recipient_list = ['sales@dreamziarah.com',]
#         send_mail(subject, message, from_email, recipient_list)

#         # Send feedback email to the sender
#         feedback_subject = "Welcome to Dream Ziarah's Travel Community!"
#         feedback_message = 'Dear Customer,\n\n'
#         feedback_message += "Congratulations and welcome to the Dream Ziarah community!\nWe're thrilled to have you on board. Get ready to receive a world of\ntravel inspiration, exclusive offers, and the latest updates right in \nyour inbox.\n\n"
#         feedback_message += "As a member, you'll enjoy:\n\n"
#         feedback_message += "Exclusive Offers: Access to members-only discounts and\npromotions.\n"
#         feedback_message += "Inspiring Stories: Immerse yourself in our captivating travel tales.\nInsider Tips: Receive valuable tips to enhance your travel\nexperiences.\n\n"
#         feedback_message += "Thank you for subscribing. Your next adventure begins now!\n\n"
#         feedback_message += "Warm regards,\n\n"
#         feedback_message += "Dream Ziarah\nCustomer Support Team."
        
#         feedback_from_email = settings.EMAIL_HOST_USER
#         feedback_recipient_list = [instance.email]
#         send_mail(feedback_subject, feedback_message, feedback_from_email, feedback_recipient_list)
