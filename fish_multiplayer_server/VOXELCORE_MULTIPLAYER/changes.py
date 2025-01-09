import asyncio
import aiofile


class ChangeManager:
    def __init__(self, filename):
        self._filename = filename
        self._queue = asyncio.Queue()
    
    async def start(self):
        async with aiofile.async_open(self._filename, "a") as file:
            while True:
                await file.write(await self._queue.get() + ";")

    async def write_change(self, line):
        await self._queue.put(line)

    async def changes_reader(self) -> asyncio.StreamReader:
        file = aiofile.AIOFile(self._filename, "r")
        await file.open()
        return file