import logging
from datetime import datetime, timezone

from telethon import TelegramClient
from telethon import events
from telethon.tl.functions.stories import SendStoryRequest
from telethon.tl.types import InputPrivacyValueAllowAll
from telethon.tl.types import User as TelegramUser

from backend.dependencies.services.gpt import get_gpt_service
from backend.dependencies.services.user import get_user_service
from domain.dto.user import CreateUserDTO
from infrastructure.enums.user_status import UserStatus
from user_bot.settings import settings

bot = TelegramClient(
    session='ai_assistant_bot',
    api_id=settings.account.api_id,
    api_hash=settings.account.api_hash,
)

bot.start(
    phone=settings.account.phone,
)

story_states = {}
story_schedule_states = {}

logger = logging.getLogger(__name__)



async def get_sender(event: events.NewMessage.Event) -> TelegramUser:
    return await bot.get_entity(event.chat_id)


# Команда для немедленной публикации истории
@bot.on(events.NewMessage(pattern='/post_story'))
async def cmd_post_story(event: events.NewMessage.Event):
    sender = await get_sender(event)
    if sender.username != 'firs_iln':
        return

    user_service = get_user_service()
    user = await user_service.get_user_by_telegram_id(sender.id)
    if not user:
        await user_service.create_user(CreateUserDTO(
            telegram_id=sender.id,
            nickname=sender.username,
        ))

        user = await user_service.get_user_by_telegram_id(sender.id)

    if user.status != UserStatus.MANAGER:
        return await event.respond('🚫 Нет доступа.')

    story_states[event.sender_id] = {}
    await event.respond('📝 Введите текст истории:')


# Команда для отложенной публикации истории
@bot.on(events.NewMessage(pattern='/schedule_story'))
async def cmd_schedule_story(event: events.NewMessage.Event):
    sender = await get_sender(event)
    if sender.username != 'firs_iln':
        return

    user_service = get_user_service()
    user = await user_service.get_user_by_telegram_id(event.chat_id)
    if user.status != UserStatus.MANAGER:
        return await event.respond('🚫 Нет доступа.')

    story_schedule_states[event.sender_id] = {}
    await event.respond('📝 Введите текст истории:')


# Общий обработчик публикаций и регистрации
@bot.on(events.NewMessage())
async def handle_messages(event):
    sender = await get_sender(event)
    if sender.username != 'firs_iln':
        return

    user_id = event.sender_id
    # Немедленная публикация
    if user_id in story_states:
        state = story_states[user_id]
        if 'text' not in state:
            state['text'] = event.raw_text
            return await event.respond('📷 Пришлите изображение или /skip:')
        if event.raw_text.strip() == '/skip':
            # await user_bot.send_message('@ampstats', state['text'])
            await event.respond('✅ Опубликовано без изображения.')
            del story_states[user_id]
            return
        if event.photo or event.document:
            media = event.photo or event.document
            if media:
                # uploaded = await user_bot.upload_file(state['file'])
                # file_id = uploaded

                await bot(SendStoryRequest(
                    peer='daria0028',
                    media=media,
                    privacy_rules=[InputPrivacyValueAllowAll()],
                ))
            # await user_bot.send_file('@ampstats', media, caption=state['text'])
            await event.respond('✅ Опубликовано с изображением.')
            del story_states[user_id]
            return
        return
    # Отложенная публикация
    if user_id in story_schedule_states:
        state = story_schedule_states[user_id]
        if 'text' not in state:
            state['text'] = event.raw_text
            return await event.respond('📷 Пришлите изображение или /skip:')
        if 'file' not in state:
            if event.raw_text.strip() == '/skip':
                state['file'] = None
            elif event.photo or event.document:
                state['file'] = event.photo or event.document
            else:
                return await event.respond('❗ Отправьте изображение или /skip.')
            return await event.respond('⏰ Введите дату и время (YYYY-MM-DD HH:MM, UTC):')
        # Шаг даты и времени
        try:
            dt = datetime.strptime(event.raw_text.strip(), '%Y-%m-%d %H:%M')
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return await event.respond('❗ Неверный формат. Повторите (YYYY-MM-DD HH:MM):')

        # story_service = get_story_service()
        # file_id = None
        if state['file']:
            uploaded = await bot.upload_file(state['file'])
            # file_id = uploaded

            await bot(SendStoryRequest(
                peer='daria0028',
                media=uploaded,
                privacy_rules=[InputPrivacyValueAllowAll()],
            ))
        # await story_service.schedule_story(text=state['text'], file_id=file_id, publish_at=dt)
        await event.respond(f'✅ История запланирована на {dt.isoformat()}')
        del story_schedule_states[user_id]
        return
    return
    # # Регистрация пользователя в базе
    # user_service = get_user_service()
    # await user_service.create_user(event.sender_id)



@bot.on(events.NewMessage(incoming=True))
async def handle_client_reply(event: events.NewMessage.Event):
    if not event.is_private:
        return
    gpt_service = get_gpt_service()
    user_service = get_user_service()

    sender_id = event.sender_id
    text = event.raw_text

    # 1) Если это команды менеджера — пропускаем (у вас уже есть логика выше)
    if text.startswith('/') and sender_id in (story_states or {}) | (story_schedule_states or {}):
        return

    # 2) Если у нас нет истории по этому user_id — начинаем новый диалог
    await gpt_service.start_gpt_conversation(sender_id)

    # 3) Посылаем текст клиента в GPT, получаем ответ
    reply = await gpt_service.get_gpt_response(
        user_id=sender_id,
        user_input=text,
    )

    # 4) Отправляем ответ обратно клиенту
    await event.respond(reply)


# # Inline-кнопки статуса сервисов
# def build_service_buttons(services):
#     buttons = []
#     for svc in services:
#         label = f"✅ {svc.name}" if svc.is_active else f"❌ {svc.name}"
#         buttons.append(Button.inline(label, data=f"toggle:{svc.name}"))
#     return [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
#
#
# # Команда: показать и переключить статус сервисов
# @user_bot.on(events.NewMessage(pattern='/services_status'))
# async def cmd_services_status(event):
#     user_service = get_user_service()
#     user = await user_service.get_user_by_telegram_id(event.sender.id)
#     if user.status != UserStatus.MANAGER:
#         return await event.respond('🚫 Нет доступа.')
#
#     analytics_service = get_analytics_service_service()
#     services = await analytics_service.get_all_services()
#     text = '🛠 Статус сервисов:'
#     await event.respond(text, buttons=build_service_buttons(services))
#
#
# # Обработка нажатия inline-кнопки для смены статуса
# @user_bot.on(events.CallbackQuery)
# async def callback_toggle(event):
#     data = event.data.decode()
#     user_service = get_user_service()
#     user = await user_service.get_user_by_telegram_id(event.sender.id)
#
#     if not data.startswith('toggle:') or user.status != UserStatus.MANAGER:
#         return
#
#     _, name = data.split(':', 1)
#     analytics_service = get_analytics_service_service()
#     services = await analytics_service.get_all_services()
#     svc = next((s for s in services if s.name == name), None)
#     if not svc:
#         return await event.answer('Сервис не найден', alert=True)
#
#     new_status = not svc.is_active
#     success = await analytics_service.update_service_active_status(svc.id, new_status)
#     if success:
#         updated = await analytics_service.get_all_services()
#         await event.edit(buttons=build_service_buttons(updated))
#         await event.answer(f"Статус {name} " + ("включён" if new_status else "отключён"))
#     else:
#         await event.answer('Ошибка при обновлении.', alert=True)

#
# @user_bot.on(events.NewMessage())
# async def auto_register(event: events.NewMessage.Event):
#     # \"\"\"
#     # При любом сообщении создаём или обновляем клиента в БД,
#     # заполняя telegram_id, nickname, а статус остаётся дефолтным.
#     # \"\"\"
#     user_service = get_user_service()
#
#     # Получаем полную информацию о пользователе
#     sender = await event.get_sender()
#     nickname = sender.username or ((sender.first_name or '') +
#                                    (' ' + (sender.last_name or '') if sender.last_name else '')).strip()
#
#     user = await user_service.get_user_by_telegram_id(event.sender.id)
#
#     if user:
#         return
#     else:
#         dto = CreateUserDTO(
#             telegram_id=event.sender_id,
#             nickname=nickname,
#         )
#
#     await user_service.create_user(dto)
