#!/usr/bin/env python3
"""
Telegram bot for getting interesting facts about nearby places.
Uses OpenAI GPT-4o-mini to generate facts based on user's location.
"""

import os
from typing import Optional

from telegram import Update, Location
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import openai

from logger_config import (
    setup_logging, 
    log_user_interaction, 
    log_openai_request, 
    log_bot_error
)
from live_location import (
    handle_live_location,
    stop_live_location,
    get_live_location_status,
    cleanup_task
)

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging(os.getenv('LOG_LEVEL', 'INFO'))

# Get tokens from environment variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing required environment variables: TELEGRAM_BOT_TOKEN or OPENAI_API_KEY")

# Configure OpenAI
openai.api_key = OPENAI_API_KEY


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    log_user_interaction(user.id, user.username, "start", f"User started the bot")
    
    welcome_message = (
        "🌍 Привет! Я бот для поиска интересных фактов о местах рядом с вами!\n\n"
        "📍 Отправьте мне свою геолокацию, и я расскажу что-то увлекательное о ближайшем месте.\n\n"
        "Для отправки геолокации нажмите на скрепку и выберите 'Местоположение'."
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user = update.effective_user
    log_user_interaction(user.id, user.username, "help", "User requested help")
    
    help_text = (
        "🤖 Как пользоваться ботом:\n\n"
        "📍 **Обычная геолокация:**\n"
        "1. Отправьте мне свою геолокацию\n"
        "2. Получите интересный факт о ближайшем месте\n\n"
        "🔄 **Живая локация (v1.1):**\n"
        "1. Отправьте живую локацию для отслеживания\n"
        "2. Получайте новые факты каждые 10 минут при движении\n\n"
        "Команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/status - статус живой локации\n"
        "/stop_live - остановить отслеживание"
    )
    await update.message.reply_text(help_text)


async def get_place_fact(latitude: float, longitude: float) -> Optional[str]:
    """Get an interesting fact about a place near the given coordinates using OpenAI."""
    try:
        prompt = f"""
        Координаты: {latitude}, {longitude}
        
        Найди интересное место рядом с этими координатами и расскажи один увлекательный факт о нём.
        Факт должен быть:
        - Необычным и малоизвестным
        - Исторически или культурно интересным
        - На русском языке
        - Не длиннее 3-4 предложений
        
        Начни ответ с названия места и его краткого описания, затем расскажи интересный факт.
        """
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        fact = response.choices[0].message.content.strip()
        log_openai_request(latitude, longitude, True)
        return fact
        
    except Exception as e:
        log_openai_request(latitude, longitude, False, str(e))
        return None


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle location messages from users (both regular and live location)."""
    user = update.effective_user
    location: Location = update.message.location
    
    if not location:
        log_user_interaction(user.id, user.username, "location_error", "No location data received")
        await update.message.reply_text("❌ Не удалось получить вашу геолокацию. Попробуйте ещё раз.")
        return
    
    # Check if this is a live location (has live_period)
    if location.live_period:
        # Handle as live location
        await handle_live_location(update, context)
        return
    
    # Handle as regular location
    log_user_interaction(
        user.id, 
        user.username, 
        "location_sent", 
        f"Coordinates: {location.latitude:.6f}, {location.longitude:.6f}"
    )
    
    # Send processing message
    processing_message = await update.message.reply_text("🔍 Ищу интересное место рядом с вами...")
    
    try:
        # Get fact from OpenAI
        fact = await get_place_fact(location.latitude, location.longitude)
        
        if fact:
            # Delete processing message
            await processing_message.delete()
            
            # Send the fact
            await update.message.reply_text(f"📍 {fact}")
            log_user_interaction(user.id, user.username, "fact_sent", "Successfully sent fact to user")
        else:
            await processing_message.edit_text(
                "😔 Извините, не удалось найти интересную информацию о вашем местоположении. "
                "Попробуйте ещё раз позже."
            )
            log_user_interaction(user.id, user.username, "fact_failed", "No fact generated")
            
    except Exception as e:
        log_bot_error(e, "handle_location")
        await processing_message.edit_text(
            "❌ Произошла ошибка при обработке вашего запроса. Попробуйте ещё раз."
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages that are not commands."""
    user = update.effective_user
    log_user_interaction(user.id, user.username, "text_message", f"Message: {update.message.text[:50]}...")
    
    await update.message.reply_text(
        "📍 Для получения интересного факта отправьте мне свою геолокацию.\n"
        "Нажмите на скрепку → Местоположение"
    )


def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", get_live_location_status))
    application.add_handler(CommandHandler("stop_live", stop_live_location))
    
    # Add location handler (handles both regular and live location)
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    
    # Add text handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start cleanup task in background
    import asyncio
    loop = asyncio.get_event_loop()
    loop.create_task(cleanup_task())

    # Start the bot
    logger.info("Starting Telegram bot with live location support...")
    logger.info("Available commands: /start, /help, /status, /stop_live")
    application.run_polling()


if __name__ == '__main__':
    main() 