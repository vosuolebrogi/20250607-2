#!/usr/bin/env python3
"""
Test script for the Location Facts Telegram Bot.
Tests basic functionality without running the full bot.
"""

import asyncio
import os
from dotenv import load_dotenv

from logger_config import setup_logging, log_user_interaction, log_openai_request
from main import get_place_fact

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging("DEBUG")


async def test_environment_variables():
    """Test if all required environment variables are set."""
    print("🔧 Testing environment variables...")
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if telegram_token:
        print(f"✅ TELEGRAM_BOT_TOKEN: {'*' * (len(telegram_token) - 8)}{telegram_token[-8:]}")
    else:
        print("❌ TELEGRAM_BOT_TOKEN: Not set")
        
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {'*' * (len(openai_key) - 8)}{openai_key[-8:]}")
    else:
        print("❌ OPENAI_API_KEY: Not set")
        
    return telegram_token and openai_key


async def test_logging():
    """Test logging functionality."""
    print("\n📝 Testing logging system...")
    
    try:
        # Test different log functions
        log_user_interaction(12345, "test_user", "test_action", "Test interaction")
        log_openai_request(55.7558, 37.6176, True)  # Moscow coordinates
        log_openai_request(40.7128, -74.0060, False, "Test error")  # NYC coordinates
        
        print("✅ Logging system working correctly")
        return True
    except Exception as e:
        print(f"❌ Logging system error: {e}")
        return False


async def test_openai_integration():
    """Test OpenAI API integration with sample coordinates."""
    print("\n🤖 Testing OpenAI integration...")
    
    # Test coordinates (Red Square, Moscow)
    test_latitude = 55.7539
    test_longitude = 37.6208
    
    try:
        fact = await get_place_fact(test_latitude, test_longitude)
        
        if fact:
            print("✅ OpenAI integration working correctly")
            print(f"📍 Sample fact: {fact[:100]}..." if len(fact) > 100 else f"📍 Sample fact: {fact}")
            return True
        else:
            print("❌ OpenAI integration failed: No fact returned")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI integration error: {e}")
        return False


async def test_imports():
    """Test if all required packages can be imported."""
    print("\n📦 Testing package imports...")
    
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
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
        
    return True


async def main():
    """Run all tests."""
    print("🧪 Starting Location Facts Bot Tests\n")
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Logging System", test_logging),
        ("OpenAI Integration", test_openai_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 Test Results Summary:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready to deploy.")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        
    return passed == total


if __name__ == "__main__":
    asyncio.run(main()) 