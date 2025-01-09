import asyncio
import sys
from server_config import Config
from changes import ChangeManager
from server import Server
from commands.handler import CommandHandler
import logging
logging.basicConfig(level=logging.INFO)

def handle_global_exception(loop, context):
    exception = context.get("exception")
    message = context.get("message", "No message provided")

    raise exception

loop = asyncio.new_event_loop()
loop.set_exception_handler(handle_global_exception)
changes = ChangeManager(Config.change_file)
loop.create_task(changes.start())

server = Server(Config, loop, changes)
loop.create_task(server.start())
loop.run_forever()