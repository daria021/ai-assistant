from abc import ABC
from uuid import UUID


class GPTServiceInterface(ABC):
    openai_api_key: str

    async def start_gpt_conversation(self, user_id: int):
        ...

    async def get_gpt_response(self, user_id: UUID, user_input: str):
        ...

    async def end_conversation(self, user_id: int):
        ...

    async def ask(self, instructions: str, input: str) -> str:
        ...
