"""
Logging configuration for the Telegram bot.
"""

import logging
import os
from datetime import datetime


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration for the bot.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            logging.FileHandler(
                f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log",
                encoding='utf-8'
            )
        ]
    )
    
    # Create logger for the bot
    logger = logging.getLogger("location_facts_bot")
    
    # Set specific log levels for external libraries to reduce noise  
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    logger.info("Logging configured successfully")
    return logger


def log_user_interaction(user_id: int, username: str, action: str, details: str = "") -> None:
    """
    Log user interactions with the bot.
    
    Args:
        user_id: Telegram user ID
        username: Telegram username
        action: Action performed (start, help, location_sent, etc.)
        details: Additional details about the interaction
    """
    logger = logging.getLogger("location_facts_bot")
    
    user_info = f"User {user_id} (@{username or 'unknown'})"
    log_message = f"{user_info} - {action}"
    
    if details:
        log_message += f" - {details}"
    
    logger.info(log_message)


def log_openai_request(latitude: float, longitude: float, success: bool, error: str = "") -> None:
    """
    Log OpenAI API requests.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude  
        success: Whether the request was successful
        error: Error message if request failed
    """
    logger = logging.getLogger("location_facts_bot")
    
    coords = f"({latitude:.6f}, {longitude:.6f})"
    
    if success:
        logger.info(f"OpenAI request successful for coordinates {coords}")
    else:
        logger.error(f"OpenAI request failed for coordinates {coords}: {error}")


def log_bot_error(error: Exception, context: str = "") -> None:
    """
    Log bot errors with context.
    
    Args:
        error: Exception that occurred
        context: Context where the error occurred
    """
    logger = logging.getLogger("location_facts_bot")
    
    error_message = f"Bot error"
    if context:
        error_message += f" in {context}"
        
    error_message += f": {str(error)}"
    
    logger.error(error_message, exc_info=True) 