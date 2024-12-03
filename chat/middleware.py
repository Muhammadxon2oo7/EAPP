from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

class UserAuthMiddleware(BaseMiddleware):
    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def __call__(self, scope, receive, send):
        # URL'dan user_id va receiver_id ni olish
        query_string = parse_qs(scope["query_string"].decode())
        user_id = query_string.get("user_id", [None])[0]
        receiver_id = query_string.get("receiver_id", [None])[0]

        if user_id:
            user = await self.get_user_by_id(user_id)
            if user:
                scope["user"] = user  # Agar foydalanuvchi topilsa
            else:
                scope["user"] = AnonymousUser()  # Agar foydalanuvchi topilmasa
        else:
            scope["user"] = AnonymousUser()  # Agar user_id bo'lmasa

        if receiver_id:
            receiver = await self.get_user_by_id(receiver_id)
            if receiver:
                scope["receiver"] = receiver  # Sherikni topish
            else:
                scope["receiver"] = None  # Agar sherik topilmasa

        return await super().__call__(scope, receive, send)
