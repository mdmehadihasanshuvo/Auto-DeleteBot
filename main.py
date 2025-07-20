import os
from telegram import Update, ChatPermissions
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    CallbackContext
)
from datetime import datetime, timedelta
import logging
import asyncio

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AutoModBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Add handlers
        self.application.add_handler(
            MessageHandler(
                filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
                self.handle_member_update
            )
        )
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & (~filters.COMMAND),
                self.handle_message
            )
        )
        self.application.add_error_handler(self.error)
    
    async def handle_member_update(self, update: Update, context: CallbackContext):
        message = update.message
        try:
            await message.delete()
            logger.info(f"Deleted member update message in {message.chat.title}")
        except Exception as e:
            logger.error(f"Error deleting member update message: {e}")
    
    async def handle_message(self, update: Update, context: CallbackContext):
        message = update.message
        chat = message.chat
        user = message.from_user
        
        if chat.type not in ['group', 'supergroup']:
            return
            
        # Skip if admin
        admins = await chat.get_administrators()
        if user.id in [admin.user.id for admin in admins]:
            return
            
        # Check for links
        if message.entities and any(entity.type == 'url' for entity in message.entities):
            await self.handle_link_violation(update, context)
    
    async def handle_link_violation(self, update: Update, context: CallbackContext):
        message = update.message
        chat = message.chat
        user = message.from_user
        
        try:
            # Delete the message
            await message.delete()
            logger.info(f"Deleted message with link from {user.id} in chat {chat.id}")
            
            # Mute the user
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            logger.info(f"Muted user {user.id} in chat {chat.id}")
            
        except Exception as e:
            logger.error(f"Error in handle_link_violation: {e}")
    
    async def error(self, update: Update, context: CallbackContext):
        logger.warning(f'Update {update} caused error {context.error}')
    
    def run(self):
        self.application.run_polling()

if __name__ == '__main__':
    TOKEN = '7653983373:AAFpgf0Dk_C0SIJbSzWPReu7ZzwbPncyv3g'  
    bot = AutoModBot(TOKEN)
    bot.run()
