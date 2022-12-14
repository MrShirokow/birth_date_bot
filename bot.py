import config
import asyncio
import aioschedule

from loguru import logger
from googlesheet_table import GoogleTable
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.utils.exceptions import ChatNotFound


logger.add(
    config.settings['LOG_FILE'],
    format='{time} {level} {message}',
    level='DEBUG',
)


class BirthDateTelegramBot(Bot):
    def __init__(self, token, parse_mode, google_table=None):
        super().__init__(token, parse_mode=parse_mode)
        self._google_table: GoogleTable = google_table


bot = BirthDateTelegramBot(
    token=config.settings['TOKEN'],
    parse_mode=types.ParseMode.HTML,
    google_table=GoogleTable('creds.json', config.settings['GOOGLESHEET_URL']),
)
dispatcher = Dispatcher(bot)
SERJ_ID = config.settings['USER_ID']


@dispatcher.message_handler(content_types=['sticker'])
async def cat_sticker_handler(message: types.Message):
    await bot.send_sticker(
        message.from_user.id, 
        sticker='CAACAgIAAxkBAAIBBWNJstZXmnX9_z310cvPE0RbloHAAAKvFgACFXAhSGhYH3WyKi5kKgQ'
    )


async def create_answer(birth_dates: dict) -> str:
    answers = []
    for value in birth_dates.values():
        if not value:
            continue
        names = ' ✨\n✨ '.join(list(value.values())[0])
        answers.append(f'❗️ {list(value.keys())[0]} - 🥳 день рождения 🥳 этих ребят:\n\n✨ {names} ✨')
    return '\n\n'.join(answers)
    

async def find_birth_dates() -> dict:
    return {
        0: bot._google_table.search_names(), 
        1: bot._google_table.search_names(time_delta=1), 
        7: bot._google_table.search_names(time_delta=7),
    } 


async def send_message():
    birth_dates = await find_birth_dates()
    answer = await create_answer(birth_dates)
    if not answer:
        return
    try:
        await bot.send_message(SERJ_ID, answer)
    except ChatNotFound as error:
        logger.info(f'{error}: sending error')
        return
    except Exception as error:
        logger.warning(error)
        return


async def scheduler():
    aioschedule.every().day.at('09:00').do(send_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True, on_startup=on_startup)
