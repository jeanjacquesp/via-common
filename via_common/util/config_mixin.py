#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import json
import os

#
# Global config as a data class
#
from abc import ABCMeta
from abc import abstractmethod


class ConfigMixIn(metaclass=ABCMeta):
    """
    A helper MixIn for loading a json config.
    """
    config = None


    def __init__(self):
        if self.__class__.config is None:
            self.__class__.config = self._read_config()
        self._init_config()


    @classmethod
    def get_config_dict(cls):
        return cls.config


    @classmethod
    @abstractmethod
    def get_config_path(cls):
        # Something like return os.getenv('CONFIG_PATH')
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def get_config_filename(cls):
        # Something like return os.getenv('CONFIG_FILENAME')
        raise NotImplementedError


    @classmethod
    @abstractmethod
    def _init_config(cls):
        raise NotImplementedError


    @classmethod
    def _read_config(cls):
        """
        Read the global config. CONFIG_PATH environment variable can hold the path to
        the config, otherwise current running directory is used.
        """
        config_path = cls.get_config_path()
        if config_path is None:
            raise AttributeError('Config PATH missing')
        # end if config_path is None
        config_filename = cls.get_config_filename()
        if config_filename is None:
            raise AttributeError('Config FILENAME missing')
        # end if config_filename is None
        config_fullpath = os.path.join(config_path, config_filename)
        if os.path.isfile(config_fullpath):
            f = open(config_fullpath)
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                raise
            except TypeError:
                raise
        else:
            raise FileNotFoundError('Config file not found at {}/{}'.format(config_path, config_filename))
        # end if os.path.isfile(config_path)
        return config
