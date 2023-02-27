import asyncio
import aioschedule as schedule
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext

from db import db_start, create_user, edit_login, get_users, get_increase_today, create_everyday_stat, \
    get_increase_month, get_increase_week
from followers import get_followers, get_month_increase_text, get_today_increase_text, check_login, \
    get_week_increase_text
from keyboards import start_kb, get_settings_kb, get_followers_kb
import exceptions
from config import TOKEN

API_TOKEN = TOKEN

bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class LoginGroup(StatesGroup):
    inst = State()
    vk = State()
    youtube = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("<b>Добро пожаловать!</b> Это бот для учёта количества подписчиков.\n\n"
                         "Выберите соцсеть для начала работы:",
                         reply_markup=start_kb, parse_mode='HTML')
    await create_user(message.from_user.id)


@dp.callback_query_handler(text=['login_settings'])
async def settings_handler(callback: types.CallbackQuery):
    kb = get_settings_kb(callback.from_user.id)
    await callback.message.answer("Выберите опцию:", reply_markup=kb)


@dp.callback_query_handler(text=['set_login'])
async def set_login_handler(callback: types.CallbackQuery):
    await LoginGroup.inst.set()
    await callback.message.answer("Введите логин для инстаграм:\n"
                                  "(измение логина приведет к удалению всей информации)")


@dp.message_handler(state=LoginGroup.inst)
async def set_login(message: types.Message, state: FSMContext):
    try:
        await check_login(message.text)
    except exceptions.NotCorrectLogin as e:
        await message.answer(str(e))
        return
    except exceptions.InstConnectionError as e:
        await message.answer(str(e))
        return

    async with state.proxy() as data:
        data['inst'] = message.text

    await edit_login(message.from_user.id, 'inst', message.text)

    kb = get_followers_kb()

    await message.answer(
        f"Добавлен логин инстаграм: {message.text}.\n\n",
        reply_markup=kb)

    await state.finish()


@dp.callback_query_handler(text=['get_followers'])
async def followers_handler(callback: types.CallbackQuery):
    try:
        followers = await get_followers(callback.from_user.id)
    except exceptions.NotCorrectLogin as e:
        await callback.message.answer(str(e))
        return
    except exceptions.InstConnectionError as e:
        await callback.message.answer(str(e))
        return

    kb = get_followers_kb()
    increase = get_increase_today(callback.from_user.id, followers)

    answer_message = f"Ваши подписчики в инстаграм: {followers}.\n\n"

    if increase is None:
        await callback.message.answer(answer_message, reply_markup=kb)
        return

    answer_message += get_today_increase_text(increase)

    await callback.message.answer(answer_message, reply_markup=kb)


@dp.callback_query_handler(text=['get_week_followers'])
async def week_followers_handler(callback: types.CallbackQuery):
    try:
        followers = await get_followers(callback.from_user.id)
    except exceptions.NotCorrectLogin as e:
        await callback.message.answer(str(e))
        return
    except exceptions.InstConnectionError as e:
        await callback.message.answer(str(e))
        return

    kb = get_followers_kb()
    increase = get_increase_week(callback.from_user.id, followers)

    if increase is None:
        await callback.message.answer("7 дней ещё не прошло.", reply_markup=kb)
        return

    answer_message = get_week_increase_text(increase)

    await callback.message.answer(answer_message, reply_markup=kb)


@dp.callback_query_handler(text=['get_month_followers'])
async def month_followers_handler(callback: types.CallbackQuery):
    try:
        followers = await get_followers(callback.from_user.id)
    except exceptions.NotCorrectLogin as e:
        await callback.message.answer(str(e))
        return
    except exceptions.InstConnectionError as e:
        await callback.message.answer(str(e))
        return

    kb = get_followers_kb()
    increase = get_increase_month(callback.from_user.id, followers)

    if increase is None:
        await callback.message.answer("30 дней ещё не прошло.", reply_markup=kb)
        return

    answer_message = get_month_increase_text(increase)

    await callback.message.answer(answer_message, reply_markup=kb)


async def send_everyday_stat():
    for user in get_users():
        try:
            followers = await get_followers(user)
        except exceptions.NotCorrectLogin:
            return
        except exceptions.InstConnectionError:
            return
        else:
            await create_everyday_stat(user, followers)

            answer_message = f"<b>Всего: {followers}🐶\n"

            today_increase = get_increase_today(user, followers)
            if today_increase is not None:
                answer_message += "\n" + get_today_increase_text(today_increase)

            week_increase = get_increase_week(user, followers)
            if week_increase is not None:
                answer_message += "\n" + get_week_increase_text(week_increase)

            month_increase = get_increase_month(user, followers)
            if month_increase is not None:
                answer_message += "\n" + get_month_increase_text(month_increase)

            answer_message += "</b>"

        await bot.send_message(chat_id=user, text=answer_message, parse_mode='HTML')


async def scheduler():
    schedule.every().day.at("23:55").do(send_everyday_stat)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    await db_start()
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
