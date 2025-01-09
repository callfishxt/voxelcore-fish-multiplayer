from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer
from .block_place import BlockPlace
from .block_break import BlockBreak
from .entity_position import EntityPosition
from .refresh_model import RefreshModel

class CommandHandler:
    def __init__(self, server:AbstractServer, changes:AbstractChangesManager):
        self._server = server
        self._changes = changes
    
    async def execute(self, player:AbstractPlayer, message:str):
        command, *args = message.split()
        match command:
            case "bp":
                await BlockPlace.handle(self._server, player, self._changes, *args)
            case "bb":
                await BlockBreak.handle(self._server, player, self._changes, *args)
            case "ep":
                await EntityPosition.handle(self._server, player, self._changes, *args)
            case "rm":
                await RefreshModel.handle(self._server, player, self._changes, *args)