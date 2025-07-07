import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message
import logging
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info(f"User connected: {self.scope['user']}")
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"User connected to conversation: {self.conversation_id}")
        undelivered = await self.get_undelivered_messages()

        for msg in undelivered:
            await self.send(text_data=json.dumps({
                "message": msg.content,
                "sender_id": msg.sender_id,
                "timestamp": msg.created_at.isoformat(),
                "delivered": False
        }))
        message_ids = [msg.id for msg in undelivered]
        await self.mark_delivered(message_ids)

    async def disconnect(self, close_code):
        logger.info(f"User disconnected: {self.scope['user']}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            sender_id = self.scope["user"].id
            if data['typing'] == "true":
                await self.channel_layer.group_send(
                self.room_group_name,
            {
                'type': 'user_typing',
                'user': sender_id,
                'typing': "true",
            }
        )
            else:
              message = data['message']
              msg_obj = await self.save_message(sender_id, message)

              await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'timestamp': str(msg_obj.created_at),
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {e}")
            await self.send(text_data=json.dumps({
                "error": "an error occurred"
            }))

    # Receive message from group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        return Message.objects.create(
            sender_id=sender_id,
            conversation_id=self.conversation_id,
            content=message
        )

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'user': event['user'],
            'typing': event['typing']
        }))

    @database_sync_to_async
    def get_undelivered_messages(self):
        return Message.objects.filter(
            conversation_id=self.conversation_id,
            delivered=False,
            sender_id=self.scope['user'].id
        )

    @database_sync_to_async
    def mark_delivered(self, message_ids):
        msg = Message.objects.filter(id__in=message_ids)
        msg.update(delivered=True)


# next we need to wire the message status system here!!
