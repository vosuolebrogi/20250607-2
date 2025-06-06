#!/usr/bin/env python3
"""
Live location functionality for version 1.1
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Set
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class LiveLocationManager:
    """Manages live location updates and periodic fact generation"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.active_users: Dict[int, dict] = {}  # user_id -> location data
        self.update_interval = 600  # 10 minutes in seconds
        self.running = False
        
    def start_live_location_tracking(self, user_id: int, chat_id: int, location: dict):
        """Start tracking live location for a user"""
        self.active_users[user_id] = {
            'chat_id': chat_id,
            'location': location,
            'last_update': datetime.now(),
            'last_fact_time': datetime.now()
        }
        
        logger.info(f"Started live location tracking for user {user_id}")
        
        # Start the update loop if not already running
        if not self.running:
            asyncio.create_task(self.update_loop())
    
    def stop_live_location_tracking(self, user_id: int):
        """Stop tracking live location for a user"""
        if user_id in self.active_users:
            del self.active_users[user_id]
            logger.info(f"Stopped live location tracking for user {user_id}")
    
    def update_location(self, user_id: int, location: dict):
        """Update location for an active user"""
        if user_id in self.active_users:
            self.active_users[user_id]['location'] = location
            self.active_users[user_id]['last_update'] = datetime.now()
            logger.info(f"Updated location for user {user_id}")
    
    async def update_loop(self):
        """Main update loop for sending periodic facts"""
        self.running = True
        
        while self.active_users:
            try:
                current_time = datetime.now()
                
                for user_id, data in list(self.active_users.items()):
                    chat_id = data['chat_id']
                    location = data['location']
                    last_fact_time = data['last_fact_time']
                    
                    # Check if it's time to send a new fact (10 minutes)
                    if current_time - last_fact_time >= timedelta(seconds=self.update_interval):
                        try:
                            # Get new fact for current location
                            fact = await self.bot.get_location_fact(
                                location['latitude'], 
                                location['longitude']
                            )
                            
                            if fact:
                                message = f"🔄 Обновление локации:\n\n🌟 {fact}"
                                await self.bot.application.bot.send_message(
                                    chat_id=chat_id,
                                    text=message
                                )
                                
                                # Update last fact time
                                self.active_users[user_id]['last_fact_time'] = current_time
                                logger.info(f"Sent periodic fact to user {user_id}")
                            
                        except Exception as e:
                            logger.error(f"Error sending periodic fact to user {user_id}: {e}")
                
                # Sleep for 1 minute before next check
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in live location update loop: {e}")
                await asyncio.sleep(60)
        
        self.running = False
        logger.info("Live location update loop stopped")

# Enhanced handlers for live location
async def handle_live_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE, live_manager: LiveLocationManager):
    """Handle start of live location sharing"""
    location_data = {
        'latitude': update.message.location.latitude,
        'longitude': update.message.location.longitude
    }
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    live_manager.start_live_location_tracking(user_id, chat_id, location_data)
    
    message = (
        "🔄 Начато отслеживание живой локации!\n\n"
        "Я буду отправлять вам новые интересные факты каждые 10 минут, "
        "пока вы делитесь своим местоположением.\n\n"
        "Чтобы остановить, отправьте команду /stop_live"
    )
    
    await update.message.reply_text(message)

async def handle_live_location_update(update: Update, context: ContextTypes.DEFAULT_TYPE, live_manager: LiveLocationManager):
    """Handle live location updates"""
    location_data = {
        'latitude': update.message.location.latitude,
        'longitude': update.message.location.longitude
    }
    
    user_id = update.effective_user.id
    live_manager.update_location(user_id, location_data)

async def handle_stop_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE, live_manager: LiveLocationManager):
    """Handle stop live location command"""
    user_id = update.effective_user.id
    live_manager.stop_live_location_tracking(user_id)
    
    message = "✅ Отслеживание живой локации остановлено."
    await update.message.reply_text(message) 