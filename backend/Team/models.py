from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

class CustomBackend(BaseBackend):
    def authenticate(self, request, name=None, phone=None, password=None):
        try:
            user = User.objects.get(name=name, phone=phone)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
