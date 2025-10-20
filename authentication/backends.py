from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from phonenumber_field.phonenumber import to_python

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        # Try email
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Try primary_phone
            try:
                user = User.objects.get(primary_phone=username)
            except User.DoesNotExist:
                # Try secondary_phone
                try:
                    user = User.objects.get(secondary_phone=username)
                except User.DoesNotExist:
                    return None
        if user and user.check_password(password):
            return user
        return None