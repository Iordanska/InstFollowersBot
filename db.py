import datetime
import sqlite3

db = sqlite3.connect("followers.db")
cursor = db.cursor()


async def db_start():
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='users'")
    table_exists = cursor.fetchone()

    if table_exists:
        return

    with open("createdb.sql", "r", encoding="utf8") as f:
        sql = f.read()
    cursor.executescript(sql)
    db.commit()


async def create_user(user_id:str):
    user = cursor.execute(f"SELECT 1 FROM users WHERE id=={user_id}").fetchone()
    if not user:
        cursor.execute("INSERT INTO users VALUES(?,?,?,?)", (user_id, '', '', '',))
        db.commit()


async def edit_login(user_id:str, codename:str, login:str):
    cursor.executescript(f"UPDATE users SET {codename} = '{login}' WHERE id=={user_id};"
                         f" DELETE FROM inst_stat WHERE user_id=={user_id};")
    db.commit()


async def create_everyday_stat(user_id:str, followers:int):
    str_date = _get_datetime_str()
    cursor.execute("INSERT INTO inst_stat('user_id', 'followers', 'created') VALUES(?,?,?)",
                   (user_id, followers, str_date,))
    db.commit()


def get_increase_today(user_id, today_followers):
    cursor.execute(
        f"SELECT followers FROM inst_stat WHERE user_id=={user_id} AND date(created) = date('now', '-1 day'); ")
    row = cursor.fetchone()
    if row is None:
        return
    yesterday_followers = row[0]
    return today_followers - yesterday_followers


def get_increase_week(user_id, today_followers):
    cursor.execute(
        f"SELECT followers FROM inst_stat WHERE user_id=={user_id} AND date(created) = date('now', '-7 day'); ")
    row = cursor.fetchone()
    if row is None:
        return
    previous_week_followers = row[0]
    return today_followers - previous_week_followers


def get_increase_month(user_id, today_followers):
    cursor.execute(
        f"SELECT followers FROM inst_stat WHERE user_id=={user_id} AND date(created) = date('now', '-30 day'); ")
    row = cursor.fetchone()
    if row is None:
        return
    previous_month_followers = row[0]
    return today_followers - previous_month_followers


def get_login(user_id, codename):
    cursor.execute(f"SELECT {codename} FROM  users WHERE id=={user_id}; ")
    row = cursor.fetchone()
    if not row:
        return None
    return str(row[0])


def get_users():
    users = []
    cursor.execute(f"SELECT id FROM users; ")
    rows = cursor.fetchall()
    for row in rows:
        users.append(row[0])
    return users


def _get_datetime_str() -> str:
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    return now
