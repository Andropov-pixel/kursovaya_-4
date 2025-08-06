from django import forms
from newsletters.models import Newsletter, Message, Recipient
from django.forms import ModelForm, BooleanField


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_custom_help_texts()
        self.apply_styling()
        self.clean_widget_attrs()

    def set_custom_help_texts(self):
        """Установление кастомных подсказок для полей"""
        password_help_texts = {
            'password1': 'Придумайте пароль, содержащий не менее 8 символов',
            'password2': 'Введите пароль еще раз'
        }
        for field_name, help_text in password_help_texts.items():
            if field_name in self.fields:
                self.fields[field_name].help_text = help_text

    def apply_styling(self):
        """Применение стилизации ко всем полям"""

        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'

            if field.help_text:
                field.widget.attrs['placeholder'] = field.help_text
                field.widget.attrs['data-help'] = field.help_text
                field.help_text = ''

            if isinstance(field, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 8,
                    'class': 'form-control message-textarea'
                })
            elif isinstance(field, forms.DateTimeField):
                field.widget = DateTimeLocalInput()
                field.widget.attrs.update({
                    'class': 'form-control datetimepicker',
                    'autocomplete': 'off'
                })

    def clean_widget_attrs(self):
        """Очистка всех нежелательных атрибутов виджета"""
        attrs_to_remove = [
            'aria-describedby',
            'data-toggle',
            'data-placement',
            'title',
            'data-original-title'
        ]

        for field in self.fields.values():
            for attr in attrs_to_remove:
                field.widget.attrs.pop(attr, None)


class NewsletterUForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Newsletter
        fields = ['start_sending', 'end_sending', 'status', 'recipient', 'message']


class NewsletterForm(StyleFormMixin, ModelForm):
    message = forms.ModelChoiceField(queryset=Message.objects.all())
    recipients = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Newsletter
        fields = ['message', 'recipients', 'start_sending', 'end_sending']


class NewsletterManagerForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Newsletter
        fields = ['status']


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        exclude = ('owner',)


class RecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Recipient
        exclude = ('owner',)