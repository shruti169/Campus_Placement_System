from django.contrib.auth.backends import ModelBackend
from .models import Registration_stu

class RegistrationStuBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Registration_stu.objects.get(eno=username)
            if user.check_password(password):
                return user
        except Registration_stu.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Registration_stu.objects.get(pk=user_id)
        except Registration_stu.DoesNotExist:
            return None