import logging
from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer

class RefreshModel:
    
    @staticmethod
    async def handle(server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *args):
        if len(args) != 1:
            logging.info(f"invalid rm command from {player.nickname}: {list(args)}")
            return
        
        msg = f"rm {args[0]}"
        await server.broadcast(msg, exclude=player.nickname)