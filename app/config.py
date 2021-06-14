import os
import asyncio
import yaml
from aiofile import async_open
from types import SimpleNamespace


class YamlConfigManager:
    def __init__(self, interval):
        self._update_interval = interval
        self._config_file = 'config.yaml'


    async def _update_loop(self, config):
        while True:
            try:
                await self._update(config)
            except Exception as e:
                print(f'Failed to update config, see you next time \n{repr(e)}')
            await asyncio.sleep(self._update_interval)


    async def _update(self, config):
        async with async_open(self._config_file, 'r') as f:
            data = yaml.safe_load(await f.read())

            config.DOMAIN = data['domain']

            database = data['database']
            config.DB_CONNECTION_STRING = f"postgresql://{database['user']}:{database['password']}@{database['host']}:{database['port']}/{database['database']}"

            security = data['security']
            config.TOKEN_SECRET_KEY = security['token_secret_key']
            config.TOKEN_NAME = security['token_name']

            admin = data['admin']
            cfg.ADMIN_LOGIN = admin['login']
            cfg.ADMIN_PASSWORD = admin['password']

            m_auth = data['m_auth']
            config.M_ACCOUNTS_ADDRESS = f"http://{m_auth['host']}:{m_auth['port']}"


    async def start(self, config):
        self._update_task = asyncio.ensure_future(self._update_loop(config))
        await self._update(config)


cfg = SimpleNamespace()

cfg.STARTUP_DB_ACTION = False
