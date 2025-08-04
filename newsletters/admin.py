from django.contrib import admin
from newsletters.models import Recipient, Message, Newsletter, NewsletterAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'message')
    list_filter = ('full_name', 'email')
    search_fields = ('full_name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'text')
    list_filter = ('subject',)
    search_fields = ('text', 'subject')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('start_sending', 'end_sending', 'status')
    list_filter = ('status', 'start_sending', 'end_sending')


@admin.register(NewsletterAttempt)
class NewsletterAttemptAdmin(admin.ModelAdmin):
    list_display = ('answer', 'status')