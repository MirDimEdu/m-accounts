import os
from types import SimpleNamespace


cfg = SimpleNamespace()


def _get_db_connection_string():
    db_connection_string = os.getenv('DB_CONNECTION_STRING')
    if db_connection_string:
        return db_connection_string
    return 'postgresql://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}'.format(**os.environ)


def _get_m_auth_connection_string(MA_HOST, MA_PORT):
    m_auth_connection_string = os.getenv('M_AUTH_CONNECTION_STRING')
    if m_auth_connection_string:
        return m_auth_connection_string
    return 'http://{MA_HOST}:{MA_PORT}'


cfg.TOKEN_SECRET_KEY = os.getenv('TOKEN_SECRET_KEY', 'X-MIRDIMEDU-KEY')
cfg.AUTH_TOKEN_NAME = os.getenv('AUTH_TOKEN_NAME', 'X-MIRDIMEDU-Token')

cfg.ADMIN_LOGIN = os.getenv('ADMIN_LOGIN', 'admin')
cfg.ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '1234')

cfg.HOST = os.getenv('ACCOUNTS_HOST', '0.0.0.0')
cfg.PORT = int(os.getenv('ACCOUNTS_PORT', '8002'))
cfg.DOMAIN = os.getenv('ACCOUNTS_DOMAIN', 'localhost')

cfg.DB_CONNECTION_STRING = _get_db_connection_string()
cfg.STARTUP_DB_ACTION = False

cfg.MA_HOST = os.getenv('M_AUTH_HOST', '127.0.0.1')
cfg.MA_PORT = int(os.getenv('M_AUTH_PORT', '8001'))
cfg.MA_ADDR = _get_m_auth_connection_string(cfg.MA_HOST, cfg.MA_PORT)
