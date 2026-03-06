import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Room, PrivateMessage
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = self.scope['user'].username

        if not self.scope['user'].is_authenticated:
            return

        saved = await self.save_message(self.room_name, self.scope['user'], message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': saved.timestamp.strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def save_message(self, room_name, user, content):
        room = Room.objects.get(name=room_name)
        return Message.objects.create(room=room, author=user, content=content)


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender_id = self.scope['user'].id
        self.receiver_username = self.scope['url_route']['kwargs']['username']

        try:
            receiver = await self.get_user(self.receiver_username)
            self.receiver_id = receiver.id
        except User.DoesNotExist:
            await self.close()
            return

        ids = sorted([self.sender_id, self.receiver_id])
        self.room_group_name = f'private_{ids[0]}_{ids[1]}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        if not self.scope['user'].is_authenticated:
            return

        receiver = await self.get_user(self.receiver_username)
        saved = await self.save_private_message(self.scope['user'], receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'private_message',
                'message': message,
                'username': self.scope['user'].username,
                'timestamp': saved.timestamp.strftime('%H:%M'),
            }
        )

    async def private_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_private_message(self, sender, receiver, content):
        return PrivateMessage.objects.create(sender=sender, receiver=receiver, content=content)
