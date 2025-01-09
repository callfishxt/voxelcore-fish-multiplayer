import logging
from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer

class BlockPlace:
    
    @staticmethod
    async def handle(server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *args):
        if len(args) != 5:
            logging.info(f"invalid block place command from {player.nickname}: {list(args)}")
            return
        
        block_id, x, y, z, rot = args
        msg = f"bp {block_id} {x} {y} {z} {rot}"
        await changes.write_change(msg)
        await server.broadcast(msg, exclude=player.nickname)