from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Allows authentication with either email or username.
    """

    def authenticate(self, request, login_input=None, password=None, **kwargs):
        user = None
        print("login input", login_input)
        # handle 'login_input = None' when request comes from django admin
        if login_input == None:
            login_input = kwargs.get('email') or kwargs.get('username')
        if password == None:
            password = kwargs.get('password')
        try:
            # Check if login input looks like an email
            if '@' in login_input:
                user = User.objects.filter(email__iexact=login_input).first()
            else:
                user = User.objects.filter(username__iexact=login_input).first()
        except User.DoesNotExist:
            return None

        if user and user.check_password(password):
            return user
        return None
