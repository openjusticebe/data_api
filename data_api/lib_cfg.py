from functools import reduce
import os
import logging
import operator
import yaml

logger = logging.getLogger(__name__)


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
        'log_level': 'info',
        'salt': os.getenv('SALT', 'OpenJusticePirates'),
        'token': os.getenv('token', 'SomeToken'),
    }

    def merge(self, cfg):
        self._config = {**self._config, **cfg}

    def dump(self):
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
