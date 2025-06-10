import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

# Replace these with your own values
api_id = 27878010  # e.g. 123456
api_hash = 'a8c3c7628be9f25001bd387bd713f6f8'
phone = '+79776721730'  # your phone number in international format

# Session file will be created as 'user.session'
session_name = 'service'


async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.connect()
    h = await client.send_code_request(phone)
    h = h.phone_code_hash
    code = input('Enter the code: ')
    try:
        await client.sign_in(phone, code, phone_code_hash=h)
    except SessionPasswordNeededError:
        await client.sign_in(password='gRizzli1980')

    string = StringSession.save(client.session)
    with open(f'{session_name}.txt', 'w') as f:
        print(string, file=f)

    await client.disconnect()

    # async with TelegramClient(session_name, api_id, api_hash) as client:
    #     h = await client.send_code_request(phone)
    #     h = h.phone_code_hash
    #     code = input('Enter the code: ')
    #     await client.sign_in(phone, code, phone_code_hash=h, password='1106')
    #     # chat_id = await client.get_entity('https://t.me/+1wnlX4i4t55jMzQy')
    #     # print(chat_id.id)
    #     string = StringSession.save(client.session)
    #     with open(f'{session_name}.txt', 'w') as f:
    #         print(string, file=f)


if __name__ == '__main__':
    # Run the async main
    asyncio.run(main())
