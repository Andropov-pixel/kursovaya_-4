import secrets
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView
from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.http import JsonResponse
from django.views import View

logger = logging.getLogger(__name__)  # Получаем логгер для текущего модуля

class UserView(View):
    def get(self, request, *args, **kwargs):
        try:
            # Логируем вход в метод и параметры запроса
            logger.info(
                f"Запрос GET /users. "
                f"Параметры: {request.GET}, "
                f"User-Agent: {request.headers.get('User-Agent')}"
            )

            # Пример обработки данных
            user_id = request.GET.get("user_id")
            if not user_id:
                logger.warning("Не передан user_id")
                return JsonResponse({"error": "user_id обязателен"}, status=400)

            # Имитация работы (например, запрос в БД)
            logger.debug(f"Поиск пользователя с id={user_id}")
            user_data = {"id": user_id, "name": "Test User"}

            # Логируем успешный ответ
            logger.info(f"Успешный ответ для user_id={user_id}")
            return JsonResponse(user_data)

        except Exception as e:
            # Логируем ошибку
            logger.error(f"Ошибка в UserView: {str(e)}", exc_info=True)
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email-confirm/{token}/'
        send_mail(
            subject='Подтверждение почты',
            message=f'Для подтверждения почты необходимо перейти по ссылке: {url}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse('users:login'))


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'


def block_user(request, pk):
    if not request.user.has_perm('users.can_block_user'):
        messages.error(request, 'У вас нет прав для блокировки пользователей')
        return redirect('newsletters:home')

    user = get_object_or_404(User, pk=pk)
    user.is_active = False
    user.save()

    action = "разблокирован" if user.is_active else "заблокирован"
    return redirect('users:user_list')