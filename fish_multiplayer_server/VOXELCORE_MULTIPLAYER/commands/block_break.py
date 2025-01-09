import logging
from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer

class BlockBreak:
    
    @staticmethod
    async def handle(server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *args):
        if len(args) != 4:
            logging.info(f"invalid block break command from {player.nickname}: {list(args)}")
            return
        
        block_id, x, y, z = args
        msg = f"bb {block_id} {x} {y} {z}"
        await changes.write_change(msg)
        await server.broadcast(msg, exclude=player.nickname)