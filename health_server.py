#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
"""

import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)


async def health_check(request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'service': 'location-facts-bot'
    })


async def root(request):
    """Root endpoint"""
    return web.json_response({
        'service': 'Location Facts Telegram Bot',
        'status': 'running'
    })


async def start_health_server(port=8000):
    """Start simple health server"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', root)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    logger.info(f"Health server started on port {port}")
    return runner 