import yaml
import os
from datetime import datetime
import pytz
import calendar


def cfg_get(config):
    def_config_file = open('config_default.yaml', 'r')
    def_config = yaml.safe_load(def_config_file)
    return {**def_config, **config}


def check_envs(env_list):
    return all(os.getenv(e) for e in env_list)


def get_now():
    now = datetime.now(pytz.utc)
    return calendar.timegm(now.utctimetuple())
