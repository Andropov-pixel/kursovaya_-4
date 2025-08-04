from django.core.management import BaseCommand
from django.utils import timezone
from newsletters.models import Newsletter
from newsletters.services import send_message


class Command(BaseCommand):
    help = 'Send current newsletters'

    def handle(self, *args, **options):
        now = timezone.now()
        try:
            newsletters = Newsletter.objects.filter(
                start_sending__lte=now,
                end_sending__gte=now,
                status__in=[Newsletter.CREATED, Newsletter.ACTIVATED]
            )
            for newsletter in newsletters:
                send_message(newsletter.pk)

                if newsletter.status == Newsletter.CREATED:
                    newsletter.status = Newsletter.ACTIVATED
                    newsletter.save()
            return 'Рассылки отправлены.'
        except Exception as ex:
            return str(ex)