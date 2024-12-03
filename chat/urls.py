from django.urls import path
from .views import ChatMessagesAPIView

urlpatterns = [
    path('chat/<int:chat_id>/messages/', ChatMessagesAPIView.as_view(), name='chat_messages'),
]
