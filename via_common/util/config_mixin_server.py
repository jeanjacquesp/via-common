#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

#
# Global config as a data class
#
from abc import ABCMeta

from via_common.util.config_mixin import ConfigMixIn


class ConfigMixInServer(ConfigMixIn, metaclass=ABCMeta):
    """
    A helper MixIn for loading a json config for a server.
    """
    config = None


    def __init__(self, server_name):
        super().__init__()
        self.server_name = server_name
        self._check_config()


    @classmethod
    def host(cls):
        return cls.config['host']


    @classmethod
    def port(cls):
        return cls.config['port']


    @classmethod
    def login(cls):
        return cls.config['login'] if 'login' in cls.config else ''


    @classmethod
    def authkey(cls):
        return cls.config['authkey']


    @classmethod
    def user_id(cls):
        return cls.config['user_id'] if 'user_id' in cls.config else ''


    @classmethod
    def timeout(cls):
        return cls.config['timeout'] if 'timeout' in cls.config else 0


    @classmethod
    def keepalive(cls):
        return cls.config['keepalive'] if 'keepalive' in cls.config else 0


    @classmethod
    def retry(cls):
        return cls.config['retry'] if 'retry' in cls.config else 10


    @classmethod
    def _check_config(cls):
        assert 'host' in cls.config
        assert 'port' in cls.config
        assert 'authkey' in cls.config
        if not isinstance(cls.config['port'], int):
            raise AttributeError('Port should be an integer')
        if 'timeout' in cls.config and not isinstance(cls.config['timeout'], int):
            raise AttributeError('Timeout should be an integer')
        if 'keepalive' in cls.config and not isinstance(cls.config['keepalive'], int):
            raise AttributeError('Keepalive should be an integer')
        if 'retry' in cls.config and not isinstance(cls.config['retry'], int):
            raise AttributeError('Retry should be an integer')
