import uuid
import httpx
from passlib.hash import bcrypt
from fastapi import Request
from datetime import datetime, timedelta

from .db import accounts
from .db import _database
from .config import cfg
from . import schemas # maybe fix to from .schemas import CurrenUser
from .errors import HTTPabort


def hash_password(password):
    return bcrypt.hash(password)


def verify_password(password, hashed_password):
    return bcrypt.verify(password, hashed_password)


async def register_admin():
    print('Register admin account in system', end='', flush=True)
    query = accounts.insert().values(role='admin', login=cfg.ADMIN_LOGIN,
                                     password=hash_password(cfg.ADMIN_PASSWORD),
                                     name='Admin',  register_time=datetime.utcnow())
    await _database.execute(query)
    print(' - OK')


@_database.transaction()
async def register_user(login, password, name):
    query = select(accounts).where(accounts.c.login == login)
    user = await _database.fetch_one(query)
    if user:
        HTTPabort(409, 'User with this login already exists')

    query = accounts.insert().values(role='user', login=login, name=name,
                                     password=hash_password(password),
                                     register_time=datetime.utcnow())
    await _database.execute(query)


async def me(current_user):
    query = select(accounts).where(accounts.c.id == current_user.account_id)
    account = await _database.fetch_one(query)

    return current_user.jsonify_info(account['login'], account['name'], account['register_time'])


async def get_account(login):
    query = select(accounts).where(accounts.c.login == login)
    account = await _database.fetch_one(query)

    return {
        'login': account['login'],
        'role': account['role'],
        'name': account['name'],
        'register_time': account['register_time']
    }


async def get_many(accounts):
    query = select(accounts).where(accounts.c.id.in_(accounts))
    accs = await _database.fetch_all(query)

    result = []
    for acc in accs:
        result.append({
            'login': acc['login'],
            'role': account['role'],
            'register_time': account['register_time']
        })
    return result


@_database.transaction()
async def change_password(current_user, old_password, new_password):
    query = select(accounts).where(accounts.c.id == current_user.account_id)
    account = await _database.fetch_one(query)

    if not verify_password(old_password, account.password):
        HTTPabort(422, 'Incorrect password')
    if old_password == new_password:
        HTTPabort(409, 'Old and new passwords are equal')

    async with httpx.AsyncClient() as ac:
        json = {
            'account_id': current_user.account_id,
            'session_id': current_user.session_id
        }
        answer = await ac.post(f'{cfg.MA_ADDR}/delete_other_sessions', json=json)

        if answer.status_code != 200:
            HTTPabort(answer.status_code, answer.json()['content'])

    query = accounts.update().where(accounts.c.id == current_user.account_id).values(password=hash_password(new_password))
    await _database.execute(query)


async def verify_account(account):
    query = select(accounts).where(accounts.c.id == current_user.account_id) if account.account_id else select(accounts).where(accounts.c.id == current_user.login)
    acc = await _database.fetch_one(query)

    if not acc:
        HTTPabort(404, 'User not found')
    if not verify_password(account.password, acc.password):
        HTTPabort(422, 'Incorrect password')

    return {
        'account_id': acc.id,
        'role': acc.role
    }
