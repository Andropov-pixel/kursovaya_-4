from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(email='kristina.rozhkova.2018@list.ru')
        user.set_password('9605')
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()