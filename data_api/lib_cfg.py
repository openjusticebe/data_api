from functools import reduce
import os
import logging
import operator
import yaml


def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)


def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value


class ConfigClass:
    """
    Application-wide config object
    """
    _config = {
        'postgresql': {
            'dsn': os.getenv('PG_DSN', 'postgres://user:pass@localhost:5432/db'),
            'min_size': 4,
            'max_size': 20
        },
        'proxy_prefix': os.getenv('PROXY_PREFIX', ''),
        'server': {
            'host': os.getenv('HOST', '127.0.0.1'),
            'port': int(os.getenv('PORT', '5000')),
            'log_level': os.getenv('LOG_LEVEL', 'info'),
            'timeout_keep_alive': 0,
        },
        'airtable': {
            'base_id': os.getenv('AIRTABLE_BASE', ''),
            'api_key': os.getenv('AIRTABLE_API', ''),
        },
        'auth': {
            'secret_key': os.getenv('AUTH_KEY', 'be62bbb060280c3955092298ab8ebbb3af0e104cd90cb969bb400e2204280ae4'),
            'algorithm': 'HS256',
            'expiration_minutes': 30,
        },
        'smtp': {
            'host': os.getenv('SMTP_HOST', 'localhost'),
            'user': os.getenv('SMTP_USER', 'user'),
            'port': os.getenv('SMTP_PORT', 'port'),
            'password': os.getenv('SMTP_PASSWORD', 'password'),
        },
        'log_level': 'info',
        'salt': os.getenv('SALT', 'OpenJusticePirates'),
        'token': os.getenv('token', 'SomeToken'),
        'oj_doc_domain': os.getenv('DOC_URI', 'http://localhost:5005'),
        'hash_max_views': os.getenv('HASH_VIEWS', 1000),
    }

    def merge(self, cfg):
        self._config = {**self._config, **cfg}

    def dump(self, logger):
        logger.debug('config: %s', yaml.dump(self._config, indent=2))

    def key(self, k):
        if isinstance(k, list):
            return get_by_path(self._config, k)
        return self._config.get(k, False)

    def set(self, k, v):
        if isinstance(k, list):
            set_by_path(self._config, k, v)
        else:
            self._config[k] = v


config = ConfigClass()
