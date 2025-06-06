"""
Live location handler for the Telegram bot.
Handles live location updates and periodic fact generation.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

from telegram import Update
from telegram.ext import ContextTypes

from logger_config import log_user_interaction, log_bot_error
from main import get_place_fact


@dataclass
class LiveLocationSession:
    """Data class to store live location session information."""
    user_id: int
    username: str
    chat_id: int
    last_update: datetime
    last_latitude: float
    last_longitude: float
    message_count: int = 0
    is_active: bool = True


class LiveLocationManager:
    """Manages live location sessions and periodic updates."""
    
    def __init__(self):
        self.active_sessions: Dict[int, LiveLocationSession] = {}
        self.update_interval = timedelta(minutes=10)
        self.min_distance_threshold = 0.001  # ~100 meters in degrees
        
    def start_session(
        self, 
        user_id: int, 
        username: str, 
        chat_id: int, 
        latitude: float, 
        longitude: float
    ) -> None:
        """Start a new live location session."""
        session = LiveLocationSession(
            user_id=user_id,
            username=username,
            chat_id=chat_id,
            last_update=datetime.now(),
            last_latitude=latitude,
            last_longitude=longitude
        )
        
        self.active_sessions[user_id] = session
        log_user_interaction(
            user_id, 
            username, 
            "live_location_started", 
            f"Started at {latitude:.6f}, {longitude:.6f}"
        )
    
    def update_location(
        self, 
        user_id: int, 
        latitude: float, 
        longitude: float
    ) -> tuple[bool, bool]:
        """
        Update location for an active session.
        
        Returns:
            tuple: (should_send_fact, location_changed_significantly)
        """
        if user_id not in self.active_sessions:
            return False, False
            
        session = self.active_sessions[user_id]
        now = datetime.now()
        
        # Calculate distance moved
        lat_diff = abs(latitude - session.last_latitude)
        lon_diff = abs(longitude - session.last_longitude)
        distance_moved = (lat_diff ** 2 + lon_diff ** 2) ** 0.5
        
        # Check if enough time has passed
        time_passed = now - session.last_update >= self.update_interval
        
        # Check if user moved significantly
        moved_significantly = distance_moved >= self.min_distance_threshold
        
        should_send_fact = time_passed and moved_significantly
        
        if should_send_fact:
            session.last_update = now
            session.last_latitude = latitude
            session.last_longitude = longitude
            session.message_count += 1
            
            log_user_interaction(
                user_id,
                session.username,
                "live_location_update",
                f"Update #{session.message_count} at {latitude:.6f}, {longitude:.6f}"
            )
        
        return should_send_fact, moved_significantly
    
    def stop_session(self, user_id: int) -> bool:
        """Stop a live location session."""
        if user_id in self.active_sessions:
            session = self.active_sessions[user_id]
            session.is_active = False
            
            log_user_interaction(
                user_id,
                session.username,
                "live_location_stopped",
                f"Session ended after {session.message_count} updates"
            )
            
            del self.active_sessions[user_id]
            return True
        return False
    
    def get_session(self, user_id: int) -> Optional[LiveLocationSession]:
        """Get active session for a user."""
        return self.active_sessions.get(user_id)
    
    def get_active_sessions_count(self) -> int:
        """Get number of active live location sessions."""
        return len(self.active_sessions)
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up sessions older than max_age_hours."""
        now = datetime.now()
        max_age = timedelta(hours=max_age_hours)
        
        inactive_sessions = [
            user_id for user_id, session in self.active_sessions.items()
            if now - session.last_update > max_age
        ]
        
        for user_id in inactive_sessions:
            self.stop_session(user_id)
            
        return len(inactive_sessions)


# Global live location manager instance
live_location_manager = LiveLocationManager()


async def handle_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle live location updates from users."""
    user = update.effective_user
    location = update.message.location
    
    if not location:
        return
    
    try:
        # Check if this is a new live location session
        session = live_location_manager.get_session(user.id)
        
        if not session:
            # Start new session
            live_location_manager.start_session(
                user.id,
                user.username,
                update.effective_chat.id,
                location.latitude,
                location.longitude
            )
            
            # Send initial fact
            processing_message = await update.message.reply_text(
                "🔄 Отслеживаю вашу живую локацию! "
                "Буду присылать новые факты каждые 10 минут при движении..."
            )
            
            fact = await get_place_fact(location.latitude, location.longitude)
            
            if fact:
                await processing_message.edit_text(f"📍 {fact}")
            else:
                await processing_message.edit_text(
                    "😔 Не удалось найти интересную информацию о вашем местоположении."
                )
        else:
            # Update existing session
            should_send_fact, moved_significantly = live_location_manager.update_location(
                user.id,
                location.latitude,
                location.longitude
            )
            
            if should_send_fact:
                # Send new fact for new location
                processing_message = await update.message.reply_text(
                    "🔍 Вы переместились! Ищу новый факт о вашем местоположении..."
                )
                
                fact = await get_place_fact(location.latitude, location.longitude)
                
                if fact:
                    await processing_message.edit_text(f"📍 {fact}")
                else:
                    await processing_message.edit_text(
                        "😔 Не удалось найти новую информацию для этого местоположения."
                    )
            elif moved_significantly:
                # User moved but not enough time passed
                await update.message.reply_text(
                    "⏰ Получу новый факт через несколько минут, когда пройдёт достаточно времени."
                )
                
    except Exception as e:
        log_bot_error(e, "handle_live_location")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке живой локации."
        )


async def stop_live_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop live location tracking for the user."""
    user = update.effective_user
    
    if live_location_manager.stop_session(user.id):
        await update.message.reply_text(
            "⏹️ Отслеживание живой локации остановлено. "
            "Спасибо за использование бота!"
        )
    else:
        await update.message.reply_text(
            "ℹ️ У вас нет активной сессии отслеживания живой локации."
        )


async def get_live_location_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get status of live location tracking."""
    user = update.effective_user
    session = live_location_manager.get_session(user.id)
    
    if session:
        time_since_last = datetime.now() - session.last_update
        minutes_since = int(time_since_last.total_seconds() / 60)
        
        status_text = (
            f"📊 Статус живой локации:\n\n"
            f"✅ Активна\n"
            f"📍 Последнее обновление: {minutes_since} мин. назад\n"
            f"🔢 Всего обновлений: {session.message_count}\n"
            f"⏱️ Следующий факт: через {max(0, 10 - minutes_since)} мин.\n\n"
            f"Используйте /stop_live для остановки отслеживания."
        )
    else:
        status_text = (
            "ℹ️ Живая локация не активна.\n\n"
            "Отправьте живую локацию для начала отслеживания."
        )
    
    await update.message.reply_text(status_text)


# Cleanup task to remove old sessions
async def cleanup_task():
    """Periodic cleanup of inactive sessions."""
    while True:
        try:
            cleaned = live_location_manager.cleanup_inactive_sessions()
            if cleaned > 0:
                print(f"Cleaned up {cleaned} inactive live location sessions")
            
            # Sleep for 1 hour
            await asyncio.sleep(3600)
            
        except Exception as e:
            log_bot_error(e, "cleanup_task")
            await asyncio.sleep(3600)  # Continue after error 