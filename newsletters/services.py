from django.utils import timezone
from django.utils.timezone import localtime
from django.core.mail import send_mail
from .models import Newsletter, NewsletterAttempt
from config.settings import EMAIL_HOST_USER


def send_message(pk, request=None):
    """Отправка рассылки по требованию"""
    newsletter = Newsletter.objects.get(pk=pk)
    now = timezone.now()

    if request and newsletter.owner != request.user:
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer=f'Рассылку пытался отправить посторонний человек: {request.user.email}',
            date_attempt=now,
        )
        return False

    subject = newsletter.message.subject
    message=newsletter.message.text
    recipient_list = [recipient.email for recipient in newsletter.recipient.all()]

    if newsletter.status == Newsletter.ENDED:
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer='Рассылка уже завершена',
            date_attempt=now,
        )
        return False

    if now < newsletter.start_sending:
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer=f'Время рассылки еще не наступило (начало - {newsletter.start_sending}, сейчас - {now})',
            date_attempt=now,
        )
        return False
    elif now > newsletter.end_sending:
        newsletter.status = Newsletter.ENDED
        newsletter.save()
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer=f'Время рассылки уже прошло (конец - {newsletter.end_sending}, сейчас - {now})',
            date_attempt=now,
        )
        return False

    if not recipient_list:
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer='Нет получателей рассылки',
            date_attempt=now,
        )
        return False

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )

        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.SUCCESS,
            answer='Рассылка отправлена',
            date_attempt=now,
        )
        if newsletter.status == Newsletter.CREATED:
            newsletter.status = Newsletter.ACTIVATED
            newsletter.save()

        return True

    except Exception as ex:
        NewsletterAttempt.objects.create(
            newsletter=newsletter,
            status=NewsletterAttempt.UNSUCCESS,
            answer=str(ex),
            date_attempt=now,
        )
        return False