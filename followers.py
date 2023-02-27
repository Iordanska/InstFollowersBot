import requests_html
import re

import db
import exceptions


async def check_login(login: str) -> bool:
    link = 'https://www.instagram.com/' + login
    request = await _get_request_inst(link)
    if _parse_inst(request):
        return True


def _parse_inst(r):
    text = r.html.find('._aacl._aacp._aacu._aacx._aad6._aade ._ac2a')

    if not text:
        raise exceptions.NotCorrectLogin("Логин не найден. Пожалуйста, проверьте логин.")

    followers = "".join(re.findall(r"title=\"([\d),]+)", text[1].html)[0].split(','))

    if followers is None:
        raise exceptions.NotCorrectLogin("Логин не найден. Пожалуйста, проверьте логин.")

    return int(followers)


async def get_followers(user_id: str) -> int:
    login = db.get_login(user_id, 'inst')
    link = 'https://www.instagram.com/' + login
    request = await _get_request_inst(link)
    followers = int(_parse_inst(request))
    return followers


async def _get_request_inst(link: str):
    asession = requests_html.AsyncHTMLSession()
    r = await asession.get(link)
    await r.html.arender(timeout=20)
    if r.status_code == 200:
        return r
    else:
        raise exceptions.InstConnectionError(
            "Не удалось установить соенинение. Попробуйте позже")


def get_today_increase_text(increase: int) -> str:
    if increase > 0:
        text = '+' + str(increase) + ' за сегодняшний день 🍀'
    elif increase == 0:
        text = str(increase) + ' за сегодняшний день.'
    else:
        text = '-' + str(increase) + ' за сегодняшний день 🔻'

    return text


def get_week_increase_text(increase: int) -> str:
    if increase > 0:
        text = '+' + str(increase) + ' за последние 7 дней! 🍏'
    elif increase == 0:
        text = str(increase) + ' за последние 7 дней.'
    else:
        text = '-' + str(increase) + ' за последние 7 дней 🔻'
    return text


def get_month_increase_text(increase: int) -> str:
    if increase > 0:
        text = "+" + str(increase) + " за месяц! 🌼"
    elif increase == 0:
        text = str(increase) + " за месяц."
    else:
        text = "-" + str(increase) + " за месяц ❗"
    return text
