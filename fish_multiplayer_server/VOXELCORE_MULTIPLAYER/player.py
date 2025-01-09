import asyncio
import logging

from annotations import AbstractServer, AbstractCommandHandler

class Player:
    def __init__(self, reader:asyncio.StreamReader, writer:asyncio.StreamWriter, server:AbstractServer, command_handler:AbstractCommandHandler, loop:asyncio.AbstractEventLoop):
        self._reader = reader
        self._writer = writer
        self._server = server
        self._loop = loop
        self._command_handler = command_handler
        self._nickname = ""
        self._msg_queue = asyncio.Queue()
    
    async def connect(self):

        player_hello = await self._reader.readuntil(b";")
        cmd, *args = player_hello.decode('utf-8')[:-1].split()
        print(cmd, *args)
        if cmd != "con" or len(args) != 5:
            raise RuntimeError("invalid player hello")
        
        self.nickname = args[0]
        self.x, self.y, self.z = (args[1], args[2], args[3])
        self.max_pack_size = args[4]

        self._queue_processor = self._loop.create_task(self._queue_listener())
        
        return self.nickname
    
    async def send_message(self, msg:str):
        print("put", msg)
        await self._msg_queue.put(msg)
        print("put1")

    async def handler(self):
        while True:
            try:
                message = (await self._reader.readuntil(b";")).decode("utf-8")[:-1]
                await self._command_handler.execute(self, message)

            except Exception as e:
                await self._server.player_disconnected(self)
                self._queue_processor.cancel()
                logging.info(f"player {self.nickname} disconnected")
                return
        
    async def _queue_listener(self):
        while True:
            msg = await self._msg_queue.get()
            logging.debug(f"send to {self.nickname}:{msg}")
            self._writer.write((msg + ";").encode("utf-8"))
            await self._writer.drain()
            logging.debug(f"send1 to {self.nickname}:{msg}")