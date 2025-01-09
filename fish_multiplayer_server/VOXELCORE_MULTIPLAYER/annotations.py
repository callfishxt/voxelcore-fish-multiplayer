import abc
import asyncio

class AbstractPlayer:
    @abc.abstractmethod
    async def send():
        pass
    

    @property
    @abc.abstractmethod
    def nickname() -> str:
        pass

class AbstractServer:
    @abc.abstractmethod
    def broadcast(self, message:str, exclude=None):
        pass
    
    @abc.abstractmethod
    async def player_disconnected(self, player:AbstractPlayer):
        pass

class AbstractChangesManager:
    @abc.abstractmethod
    async def changes_reader() -> asyncio.StreamReader:
        pass

    @abc.abstractmethod
    async def write_change(self, data:str):
        pass

class AbstractCommandHandler:
    @abc.abstractmethod
    async def handle(self, server:AbstractServer, player:AbstractPlayer, changes:AbstractChangesManager, *data):
        pass

