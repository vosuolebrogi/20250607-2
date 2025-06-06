#!/usr/bin/env python3
"""
Simple test script for the Location Facts Bot
"""

import asyncio
import os
from dotenv import load_dotenv
from bot import LocationFactBot

# Load environment variables
load_dotenv()

async def test_openai_integration():
    """Test OpenAI integration with sample coordinates"""
    print("🧪 Testing OpenAI integration...")
    
    try:
        bot = LocationFactBot()
        
        # Test with Moscow coordinates
        moscow_lat, moscow_lon = 55.7558, 37.6176
        fact = await bot.get_location_fact(moscow_lat, moscow_lon)
        
        if fact:
            print(f"✅ OpenAI integration works!")
            print(f"📍 Sample fact for Moscow: {fact[:100]}...")
        else:
            print("❌ OpenAI integration failed - no fact returned")
            
    except Exception as e:
        print(f"❌ OpenAI integration error: {e}")

def test_environment_variables():
    """Test if required environment variables are set"""
    print("🧪 Testing environment variables...")
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if telegram_token:
        print("✅ TELEGRAM_BOT_TOKEN is set")
    else:
        print("❌ TELEGRAM_BOT_TOKEN is not set")
    
    if openai_key:
        print("✅ OPENAI_API_KEY is set")
    else:
        print("❌ OPENAI_API_KEY is not set")
    
    return bool(telegram_token and openai_key)

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing package imports...")
    
    try:
        import telegram
        print("✅ python-telegram-bot imported successfully")
    except ImportError as e:
        print(f"❌ python-telegram-bot import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting Location Facts Bot Tests\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Package import tests failed. Run: pip install -r requirements.txt")
        return
    
    print()
    
    # Test environment variables
    if not test_environment_variables():
        print("\n❌ Environment variable tests failed. Create .env file with required tokens.")
        return
    
    print()
    
    # Test OpenAI integration
    await test_openai_integration()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Next steps:")
    print("1. Make sure your .env file contains valid tokens")
    print("2. Run the bot: python bot.py")
    print("3. Test in Telegram by sending /start to your bot")

if __name__ == "__main__":
    asyncio.run(main()) 