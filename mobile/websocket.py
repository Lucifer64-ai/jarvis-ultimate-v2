"""
WebSocket µ²µ JARVIS для real-time ¾±½¾²»µ½¸¹
"""

import asyncio
import json
import websockets
from typing import Set, Dict
import threading


class WebSocketServer:
    """WebSocket µ²µ для real-time ²·¸."""

    def __init__(self, brain):
        self.brain = brain
        self.port = brain.config.websocket_port
        self.clients: Set = set()
        self.running = False

    async def handler(self, websocket, path):
        """±°±¾º° WebSocket ¿¾´º»µ½¸¹."""
        self.clients.add(websocket)
        self.brain.logger.info(f"¾²¾µ WebSocket ¿¾´º»µ½¸µ. µ³¾ º»¸µ½¾²: {len(self.clients)}")
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({"error": "Invalid JSON"}))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            self.brain.logger.info(f"»¸µ½ ¾º»µ½. µ³¾ º»¸µ½¾²: {len(self.clients)}")

    async def _process_message(self, websocket, data: Dict):
        """±°±¾º° ²¾´µ³¾ ¾¾±µ½¸."""
        msg_type = data.get("type")
        
        if msg_type == "command":
            command = data.get("command", "")
            result = self.brain.execute_command(command)
            await websocket.send(json.dumps({
                "type": "command_result",
                "data": result
            }))
        
        elif msg_type == "status":
            status = self.brain.get_status()
            await websocket.send(json.dumps({
                "type": "status",
                "data": status
            }))
        
        elif msg_type == "subscribe":
            # ¾´¿¸º° ½° ¾±½¾²»µ½¸
            await websocket.send(json.dumps({
                "type": "subscribed",
                "message": "¾´¿¸º° ½° ¾±½¾²»µ½¸ °º¸²¸¾²°½°"
            }))

    async def broadcast(self, message: Dict):
        """¿°²º° ¾¾±µ½¸ ²µ¼ ¿¾´º»µ½½¼ º»¸µ½°¼."""
        if self.clients:
            await asyncio.wait([
                client.send(json.dumps(message))
                for client in self.clients
            ])

    async def start_server(self):
        """°¿º WebSocket µ²µ°."""
        self.running = True
        server = await websockets.serve(self.handler, "0.0.0.0", self.port)
        self.brain.logger.info(f"WebSocket µ²µ ·°¿µ½ ½° ¿¾ {self.port}")
        await server.wait_closed()

    def start(self):
        """°¿º ² ¾´µ»½¾¼ ¿¾¾ºµ."""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_server())
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

    def stop(self):
        """°½¾²º° µ²µ°."""
        self.running = False
