import logging
from dataclasses import dataclass
from uuid import UUID

from openai import OpenAI
from backend.abstractions.services.gpt import GPTServiceInterface
from user_bot.settings import settings


logger = logging.getLogger(__name__)

@dataclass
class GPTService(GPTServiceInterface):
    client: OpenAI = OpenAI(
        api_key=settings.assistant.openai_api_key,
    )

    # храним историю диалога для каждого user_id
    user_conversations: dict[UUID, list[dict]] = None

    def __post_init__(self):
        # инициализируем словарь, чтобы избежать разделяемого mutable по умолчанию
        if self.user_conversations is None:
            self.user_conversations = {}

    async def start_gpt_conversation(self, user_id: UUID):
        self.user_conversations[user_id] = []

    async def get_gpt_response(self, user_id: UUID, user_input: str) -> str:
        # получаем или создаём историю
        history = self.user_conversations.setdefault(user_id, [])

        # добавляем новое сообщение от пользователя
        history.append({"role": "user", "content": user_input})

        logger.info(f"Отправляем в ассистент ({settings.assistant.assistant_id}): {history}")

        # assistant = self.client.beta.assistants.retrieve(settings.assistant.assistant_id)

        thread = self.client.beta.threads.create()

        logger.info(f"сообщения из контекста: {history}")
        for msg in history:
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role=msg['role'],
                content=msg["content"],
            )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=settings.assistant.assistant_id,
        )

        if run.status == 'completed':
            msgs_page = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            last_message = msgs_page.data[0]
            reply = last_message.content[0].text.value
            logger.info(f"Ответ ассистента: {reply}")
        else:
            logger.error(run.status)
            return

        # сохраняем в историю
        history.append({"role": "assistant", "content": reply})
        self.user_conversations[user_id] = history

        return reply

    async def end_conversation(self, user_id: UUID) -> bool:
        return self.user_conversations.pop(user_id, None) is not None


    #
    # async def ask(self, instructions: str, input: str) -> str:
    #     # Формируем список именно из параметров нужных типов
    #     messages = [
    #         ChatCompletionSystemMessageParam(content=instructions),
    #         ChatCompletionUserMessageParam(content=input),
    #     ]
    #     logger.info(f"Одноразовый запрос ассистенту {settings.assistant.assistant_id}: {messages}")
    #
    #     response = self.client.chat.completions.create(
    #         model=settings.assistant.assistant_id,
    #         messages=messages
    #     )
    #
    #     reply = response.choices[0].message.content
    #     logger.info(f"Ответ ассистента: {reply}")
    #     return reply
