from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class EmailAuthBackend:

    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, id_user):
        try:
            return User.objects.get(pk=id_user)
        except User.DoesNotExist:
            return None
