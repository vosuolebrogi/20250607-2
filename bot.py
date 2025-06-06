#!/usr/bin/env python3
"""
Telegram bot that provides interesting facts about places near user's location.
"""

import os
import logging
import asyncio
from typing import Optional
from telegram import Update, Location
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)
from dotenv import load_dotenv
import openai
from health_server import run_health_server

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

class LocationFactBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot command and message handlers"""
        # Commands
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Location messages
        self.application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
        
        # Text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        welcome_message = (
            "🌍 Добро пожаловать в бот интересных фактов о местах!\n\n"
            "Отправьте мне свою геолокацию, и я расскажу вам интересный факт "
            "о ближайшем к вам месте.\n\n"
            "Для отправки геолокации:\n"
            "📍 Нажмите на скрепку → Геопозиция → Отправить мое местоположение\n\n"
            "Используйте /help для получения дополнительной информации."
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_message = (
            "🤖 Как использовать бот:\n\n"
            "1. Отправьте свою геолокацию через Telegram\n"
            "2. Я найду интересное место рядом с вами\n"
            "3. Получите увлекательный факт об этом месте!\n\n"
            "Команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать это сообщение\n\n"
            "💡 Совет: Убедитесь, что у вас включены службы геолокации"
        )
        await update.message.reply_text(help_message)
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle location messages"""
        location: Location = update.message.location
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        logger.info(f"Received location from user {username} ({user_id}): "
                   f"lat={location.latitude}, lon={location.longitude}")
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            # Get interesting fact about the location
            fact = await self.get_location_fact(location.latitude, location.longitude)
            
            if fact:
                response = f"🌟 Интересный факт о вашем местоположении:\n\n{fact}"
            else:
                response = ("😔 Извините, не удалось найти интересный факт о вашем "
                          "местоположении. Попробуйте еще раз или выберите другое место.")
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error processing location: {e}")
            await update.message.reply_text(
                "😞 Произошла ошибка при обработке вашего местоположения. "
                "Попробуйте еще раз через некоторое время."
            )
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle text messages"""
        message = (
            "📍 Пожалуйста, отправьте мне свою геолокацию, чтобы получить "
            "интересный факт о ближайшем месте.\n\n"
            "Для отправки геолокации нажмите на скрепку и выберите 'Геопозиция'."
        )
        await update.message.reply_text(message)
    
    async def get_location_fact(self, latitude: float, longitude: float) -> Optional[str]:
        """Get interesting fact about location using OpenAI"""
        try:
            prompt = f"""
            Найди интересное и необычное место или факт рядом с координатами {latitude}, {longitude}.
            
            Требования к ответу:
            1. Ответ должен быть на русском языке
            2. Не более 500 символов
            3. Интересный и познавательный факт
            4. Без упоминания точных координат в ответе
            5. Если это крупный город, расскажи о менее известных, но интересных местах или фактах
            6. Начни ответ сразу с факта, без вступлений
            
            Примеры хороших ответов:
            - "В этом районе находится самый старый дуб города, которому более 300 лет..."
            - "Здесь проходила древняя торговая дорога, соединявшая..."
            - "В паре километров отсюда находится уникальный памятник архитектуры..."
            """
            
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "Ты эксперт по истории, географии и интересным местам. Твоя задача - находить увлекательные факты о любых локациях."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error getting location fact from OpenAI: {e}")
            return None
    
    async def run(self):
        """Run the bot"""
        logger.info("Starting Location Facts Bot...")
        
        # Start health server for Railway
        run_health_server(port=int(os.getenv('PORT', 8000)))
        
        await self.application.run_polling(drop_pending_updates=True)

def main():
    """Main function"""
    try:
        bot = LocationFactBot()
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main() 