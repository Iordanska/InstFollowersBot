from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db import get_login

start_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[
    [InlineKeyboardButton(text='Инстаграм',
                          callback_data='set_login')],
    # [ InlineKeyboardButton(text='ВКонтакте',
    #                     callback_data = 'vk')],
    # [InlineKeyboardButton(text='Ютуб',
    #                       callback_data = 'youtube')]
])


def get_settings_kb(user_id):
    buttons = []
    login = get_login(user_id, 'inst')
    if login is None:
        buttons.append([InlineKeyboardButton(text='Добавить логин инстаграм',
                                             callback_data='set_login')],
                       )
    else:
        buttons.append([InlineKeyboardButton(text='Изменить логин инстаграм',
                                             callback_data='set_login')]
                       )
        buttons.append([InlineKeyboardButton(text='Назад',
                                             callback_data='get_followers')])
    settings_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)
    return settings_kb


def get_followers_kb():
    buttons = [[InlineKeyboardButton(text='Подписчики инстаграм',
                                     callback_data='get_followers')],
               [InlineKeyboardButton(text='За 7 дней',
                                     callback_data='get_week_followers')],
               [InlineKeyboardButton(text='За 30 дней',
                                     callback_data='get_month_followers')],
               [InlineKeyboardButton(text='Настройки',
                                     callback_data='login_settings')], ]

    # if  get_login(user_id, 'vk') is not None:
    #      buttons.append([InlineKeyboardButton(text='Узнать Вконтакте',
    #                            callback_data='get_vk')])
    # if  get_login(user_id, 'youtube') is not None:
    #      buttons.append([InlineKeyboardButton(text='Узнать Ютуб',
    #                            callback_data='get_youtube')])
    followers_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=buttons)
    return followers_kb
