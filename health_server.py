#!/usr/bin/env python3
"""
Simple health check server for Railway deployment
"""

import asyncio
import logging
from aiohttp import web, web_runner
import threading

logger = logging.getLogger(__name__)

class HealthServer:
    def __init__(self, port=8000):
        self.port = port
        self.app = web.Application()
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/', self.root)
        self.runner = None
        self.site = None
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'location-facts-bot'
        })
    
    async def root(self, request):
        """Root endpoint"""
        return web.json_response({
            'service': 'Location Facts Telegram Bot',
            'status': 'running'
        })
    
    async def start(self):
        """Start the health server"""
        try:
            self.runner = web_runner.AppRunner(self.app)
            await self.runner.setup()
            self.site = web_runner.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            logger.info(f"Health server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start health server: {e}")
    
    async def stop(self):
        """Stop the health server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Health server stopped")

def run_health_server(port=8000):
    """Run health server in a separate thread"""
    def start_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        server = HealthServer(port)
        loop.run_until_complete(server.start())
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(server.stop())
            loop.close()
    
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    logger.info(f"Health server thread started on port {port}")
    return thread 