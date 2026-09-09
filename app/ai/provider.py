from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def generate(self,promt:str) -> str:
        pass