from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name='chats_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='chats_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"

    @classmethod
    def get_or_create_chat(cls, user1, user2):
        """Get or create a chat between two users"""
        chat, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        ) if user1.id < user2.id else cls.objects.get_or_create(
            user1=user2,
            user2=user1
        )
        return chat


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='message_images/', blank=True, null=True)  # Rasmni saqlash
    is_read = models.BooleanField(default=False)  # O'qilgan status

    def __str__(self):
        return f"Message from {self.sender} in chat {self.chat.id}"


