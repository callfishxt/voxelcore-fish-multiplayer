import logging
from annotations import AbstractChangesManager, AbstractServer, AbstractPlayer

class ChatSendMessage:
    
    @staticmethod
    async def handle(server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *args):
        if len(args) < 1:
            logging.info(f"invalid chat send message command from {player.nickname}: {list(args)}")
            return
        
        message = args[0]
        msg = f"chat {player.nickname} {message}"

        await server.broadcast(msg, exclude=player.nickname)