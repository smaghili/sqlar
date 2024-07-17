from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import aiofiles
import os

from tools.language.handler import MESSAGE
from tools.db import db
from tools.config import BOT_TOKEN, ADMIN_CHATID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
@dp.message(Command("help"))
async def send_welcome(message: types.Message, bot: Bot):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Marzban Documentation", 
            web_app=WebAppInfo(url="https://gozargah.github.io/marzban/fa/examples/mysql-queries")
        )]
    ])

    if message.chat.id == int(ADMIN_CHATID):
        await message.reply(await MESSAGE('START'), reply_markup=keyboard)
    else:
        await message.reply(await MESSAGE('BLOCK'))

@dp.message()
async def handle_sql_query(message: types.Message, bot: Bot):
    if message.chat.id != int(ADMIN_CHATID):
        await message.reply(await MESSAGE('BLOCK'))
        return

    try:
        await db.connect()
        query = message.text
        results = await db.execute_query(query)

        num_results = len(results)
        if num_results == 0:
            response = await MESSAGE('SUCCESS_NO_MESSAGE')
            await message.reply(response)
        else:
            chunks = [results[i:i + 5] for i in range(0, num_results, 5)]
            for chunk in chunks:
                response = "\n".join(str(row) for row in chunk)
                await message.reply(response)

    except Exception as e:
        await message.reply(f"<b>{await MESSAGE('ERROR')}</b>\n\n<pre>{str(e)}</pre>", parse_mode=ParseMode.HTML)
    finally:
        await db.disconnect()

@dp.message(content_types=types.ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    if message.chat.id != int(ADMIN_CHATID):
        await message.reply(await MESSAGE('BLOCK'))
        return

    document = message.document
    if document.mime_type == 'application/sql' or document.file_name.endswith('.sql'):
        file_path = f"/var/lib/marzban/mysql/db-backup/{document.file_name}"
        
        await bot.download_file_by_id(document.file_id, file_path)
        await message.reply(f"File '{document.file_name}' has been saved successfully.")
    else:
        await message.reply("Please upload a valid .sql file.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
