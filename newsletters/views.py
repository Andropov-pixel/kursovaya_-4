from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from config import settings
from .forms import NewsletterForm, NewsletterUForm, MessageForm, RecipientForm, NewsletterManagerForm
from .models import Recipient, Message, Newsletter, NewsletterAttempt
from .services import send_message
from django.core.cache import cache


def home(request):
    context = cache.get('home')

    if not context:
        total_newsletters = Newsletter.objects.count()
        active_newsletters = Newsletter.objects.filter(status='Запущена').count()

        # Получаем количество уникальных email-адресов получателей
        unique_recipients = Recipient.objects.values('email').distinct().count()

        context = {
            'total_newsletters': total_newsletters,
            'active_newsletters': active_newsletters,
            'unique_recipients': unique_recipients,
        }
        cache.set('home', context, 60 * 15)

    return render(request, 'newsletters/home.html', context)


class RecipientListView(ListView):
    model = Recipient
    template_name = 'newsletters/recipient/recipient_list.html'


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'newsletters/recipient/recipient_detail.html'


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'newsletters/recipient/recipient_form.html'
    success_url = reverse_lazy('newsletters:recipient_list')

    def form_valid(self, form):
        recipient = form.save()
        user = self.request.user
        recipient.owner = user
        recipient.save()
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'newsletters/recipient/recipient_form.html'
    success_url = reverse_lazy('newsletters:recipient_list')

    def get_success_url(self):
        return reverse('newsletters:recipient_detail', args=[self.kwargs.get('pk')])


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'newsletters/recipient/recipient_confirm_delete.html'
    success_url = reverse_lazy('newsletters:recipient_list')


class MessageListView(ListView):
    model = Message
    template_name = 'newsletters/message/message_list.html'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'newsletters/message/message_detail.html'


class MessageCreateView(CreateView):
    model = Message
    template_name = 'newsletters/message/message_form.html'
    form_class = MessageForm
    success_url = reverse_lazy('newsletters:message_list')

    def form_valid(self, form):
        message = form.save()
        user = self.request.user
        message.owner = user
        message.save()
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    template_name = 'newsletters/message/message_form.html'
    form_class = MessageForm
    success_url = reverse_lazy('newsletters:message_list')

    def get_success_url(self):
        return reverse('newsletters:message_detail', args=[self.kwargs.get('pk')])


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'newsletters/message/message_confirm_delete.html'
    success_url = reverse_lazy('newsletters:message_list')


class NewsletterListView(ListView):
    model = Newsletter
    template_name = 'newsletters/newsletter/newsletter_list.html'


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = 'newsletters/newsletter/newsletter_detail.html'

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager').exists():
            queryset = cache.get('newsletter_list_for_manager')
            if not queryset:
                queryset = super().get_queryset()
                cache.set('newsletter_list_for_manager', queryset, 60 * 15)  # Кешируем данные на 15 минут
            return queryset
        return super().get_queryset()


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterUForm
    template_name = 'newsletters/newsletter/newsletter_form.html'
    success_url = reverse_lazy('newsletters:newsletter_list')

    def form_valid(self, form):
        newsletter = form.save()
        user = self.request.user
        newsletter.owner = user
        newsletter.save()
        return super().form_valid(form)


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterUForm
    template_name = 'newsletters/newsletter/newsletter_form.html'
    success_url = reverse_lazy('newsletters:newsletter_list')

    def get_success_url(self):
        return reverse('newsletters:newsletter_detail', args=[self.kwargs.get('pk')])

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return NewsletterUForm
        elif user.groups.filter(name='Manager').exists():
            return NewsletterManagerForm
        raise PermissionDenied


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = 'newsletters/newsletter/newsletter_confirm_delete.html'
    success_url = reverse_lazy('newsletters:newsletter_list')


class NewsletterAttemptListView(ListView):
    model = NewsletterAttempt
    template_name = 'newsletters/newsletter_attempt_list.html'
    context_object_name = 'attempts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempts = self.get_queryset()
        context['total_attempts'] = attempts.count()
        context['successful_attempts'] = attempts.filter(status='Успешно').count()
        context['unsucessful_attempts'] = attempts.filter(status='Не успешно').count()
        context['sending_mails'] = sum(
            attempt.newsletter.recipient.count()
            for attempt in attempts.filter(status='Успешно')
        )
        return context

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Вы не авторизованы")

        cache_key = f'newsletter_attempts_user_{self.request.user.pk}'
        queryset = cache.get(cache_key)
        if not queryset:
            queryset = NewsletterAttempt.objects.filter(newsletter__owner=self.request.user).order_by('-date_attempt')
            cache.set(cache_key, queryset, 60 * 15)

        return queryset


class NewsletterAttemptDetailView(DetailView):
    model = NewsletterAttempt
    template_name = 'newsletters/newsletter_attempt_detail.html'


class SendNewsletterView(View):
    template_name = 'newsletters/send_newsletter.html'

    def get(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk, owner=request.user)

        success = send_message(newsletter.pk, request)

        if success:
            print('Рассылка успешно отправлена')
        else:
            print('Рассылка не отправлена')

        return redirect('newsletters:newsletter_list')