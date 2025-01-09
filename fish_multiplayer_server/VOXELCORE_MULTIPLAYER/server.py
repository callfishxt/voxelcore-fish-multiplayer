from annotations import AbstractChangesManager
from server_config import Config
from commands.handler import CommandHandler
import asyncio
import logging
from player import Player

class Server:
    def __init__(self, config:Config, loop:asyncio.BaseEventLoop, changes_manager:AbstractChangesManager):
        self._config = config
        self._loop = loop
        self._command_handler = CommandHandler(self, changes_manager)
        self._changes_manager = changes_manager
        self._players = {}
    
    async def start(self):
        logging.info(f"starting server on {self._config.host}:{self._config.port}")
        server = await asyncio.start_server(self._client_handler, self._config.host, self._config.port)
        async with server:
            await server.serve_forever()
    
    async def player_disconnected(self, player):
        del self._players[player.nickname]
        await self.broadcast(f"dcon {player.nickname}")
    
    async def broadcast(self, msg, exclude:str=None):
        logging.debug(f"broadcast:{msg} {exclude}")
        for nick, player in self._players.items():
            if exclude is None or exclude != nick:
                await player.send_message(msg)
    
    async def _client_handler(self, reader, writer):
        addr = writer.get_extra_info("peername")
        logging.info(f"{addr} connecting")
        player = Player(reader, writer, self, self._command_handler, self._loop)
        try:
            nickname = await player.connect()
        except Exception as msg:
            logging.error(f"player connection failed {addr}: {msg}")
            raise msg

        changes = await self._changes_manager.changes_reader()
        while True:
            data = await changes.read(1024)
            await player.send_message(data)
            if len(data) < 1024:
                break
        
        self._players[nickname] = player
        logging.info(f"player {addr} {nickname} connected")
        await player.handler()