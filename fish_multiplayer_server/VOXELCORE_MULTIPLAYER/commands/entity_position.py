import logging
from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer

class EntityPosition:
    
    @staticmethod
    async def handle(server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *args):
        if len(args) != 4:
            logging.info(f"invalid entity position command from {player.nickname}: {list(args)}")
            return
        
        x, y, z, x_rot = args
        msg = f"ep {player.nickname} {x} {y} {z} {x_rot}"
        await server.broadcast(msg, exclude=player.nickname)