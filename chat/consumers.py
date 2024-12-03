import json
from django.utils.timezone import now, localtime
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
import urllib.parse
from django.conf import settings

User = get_user_model()

import redis

# Redis ulanishini sozlash
# redis_client = redis.StrictRedis.from_url("redis://127.0.0.1:6379/0", decode_responses=True)
redis_client = redis.StrictRedis.from_url("redis://redis:6379/0", decode_responses=True)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.receiver_id = self.get_receiver_id()

        if not self.receiver_id:
            await self.close()
            return

        self.receiver = await self.get_user_by_id(self.receiver_id)

        if not self.receiver:
            await self.close()
            return

        self.chat = await self.get_or_create_chat(self.user, self.receiver)

        self.room_group_name = f"chat_{self.chat.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.set_user_online_status(True)
        await self.mark_all_unread_messages_as_read()
        await self.add_user_to_chat(self.user)

        participants_count = await self.get_chat_participants_count()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'send_participants_count',
            'count': participants_count
        })

    async def disconnect(self, close_code):
        await self.set_user_online_status(False)
        await self.remove_user_from_chat(self.user)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        participants_count = await self.get_chat_participants_count()

        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'send_participants_count',
            'count': participants_count
        })

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get("message")
        image = text_data_json.get("image")  # Yangi rasm ma'lumotini olish

        sent_at = localtime(now())

        # Xabarni saqlash va rasmni ifodalash
        message = await self.save_message(self.chat, self.user, message_content, sent_at, image)

        # Xabarni grupaga yuborish
        await self.channel_layer.group_send(self.room_group_name, {
            'type': 'chat_message',
            'message': self.format_message(message, sent_at)
        })

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

    def format_message(self, message, sent_at):
        """Xabarni formatlash uchun metod."""
        message_data = {
            'sender_id': message.sender.id,
            'sender_name': message.sender.username,
            'chat_id': message.chat.id,
            'content': message.content,
            'created_at': sent_at.isoformat()
        }

        if message.image:
            # Get the absolute URL for the image
            image_url = message.image.url
            if not image_url.startswith('http'):
                # Prepend the base URL if it's not already a full URL
                image_url = f"{settings.SITE_URL}{image_url}"
            message_data['image_url'] = image_url

        return message_data

    @sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def get_or_create_chat(self, user1, user2):
        return Chat.get_or_create_chat(user1, user2)

    @sync_to_async
    def save_message(self, chat, user, message_content, sent_at, image):
        """Yangi xabarni bazaga saqlash."""
        # Agar rasm mavjud bo'lsa, uni saqlash
        message = Message.objects.create(
            chat=chat,
            sender=user,
            content=message_content,
            created_at=sent_at
        )

        if image:
            message.image = image  # Rasmni saqlash
            message.save()

        return message

    @sync_to_async
    def mark_all_unread_messages_as_read(self):
        unread_messages = Message.objects.filter(
            chat=self.chat,
            is_read=False,
        ).exclude(sender=self.user)
        unread_messages.update(is_read=True)

    @sync_to_async
    def set_user_online_status(self, status):
        self.user.is_online = status
        self.user.save()

    @sync_to_async
    def add_user_to_chat(self, user):
        redis_client.sadd(f"chat_{self.chat.id}_participants", user.id)

    @sync_to_async
    def remove_user_from_chat(self, user):
        redis_client.srem(f"chat_{self.chat.id}_participants", user.id)

    @sync_to_async
    def get_chat_participants_count(self):
        participants = redis_client.smembers(f"chat_{self.chat.id}_participants")
        return len(participants)

    async def send_participants_count(self, event):
        count = event['count']
        await self.send(text_data=json.dumps({
            'type': 'participants_count',
            'count': count
        }))

    def get_receiver_id(self):
        query_string = self.scope["query_string"].decode()
        params = urllib.parse.parse_qs(query_string)
        return params.get('receiver_id', [None])[0]
