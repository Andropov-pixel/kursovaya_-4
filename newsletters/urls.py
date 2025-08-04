from django.urls import path
from newsletters.apps import NewslettersConfig
from newsletters import views

app_name = NewslettersConfig.name

urlpatterns = [
    path('', views.home, name='home'),

    path('recipient_list/', views.RecipientListView.as_view(), name='recipient_list'),
    path('recipient/<int:pk>/detail/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/create/', views.RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/update/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),

    path('newsletter_list/', views.NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletter/<int:pk>/detail/', views.NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter/create/', views.NewsletterCreateView.as_view(), name='newsletter_create'),
    path('newsletter/<int:pk>/update/', views.NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletter/<int:pk>/delete/', views.NewsletterDeleteView.as_view(), name='newsletter_delete'),

    path('message_list/', views.MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/detail/', views.MessageDetailView.as_view(), name='message_detail'),
    path('message/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    path('newsletter_attempt_list/', views.NewsletterAttemptListView.as_view(), name='newsletter_attempt_list'),
    path('newsletter_attempt/<int:pk>/detail/', views.NewsletterAttemptDetailView.as_view(), name='newsletter_attempt_detail'),
    path('newsletter/<int:pk>/send/', views.SendNewsletterView.as_view(), name='send_newsletter'),
]