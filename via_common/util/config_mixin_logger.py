#  Copyright 2019 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

#
# Global config as a data class
#
import multiprocessing
import multiprocessing.queues
from abc import ABCMeta
from abc import abstractmethod

from via_common.util.config_mixin import ConfigMixIn


class ConfigMixInLogger(ConfigMixIn, metaclass=ABCMeta):
    """
    A helper MixIn for loading a json config for the logger.

    This class works in conjunction with eht LoggerRManager by providing
        a method to inject the logger queue into the logging config.
    """
    logger_queue = None
    config_logger = None  # the dictionary


    def __init__(self, logger_queue=None):
        super().__init__()
        self.__class__.config_logger = self.get_config_dict()
        self._init_config_logger(logger_queue)
        # When a child process start running, it needs the config to set the shared queues
        # We need then to set the logger_queue once it has been retrieved
        if self.__class__.logger_queue is None and logger_queue:
            self.set_logger_queue(logger_queue)


    @classmethod
    @abstractmethod
    def _init_config_logger(cls, logger_queue):
        raise NotImplementedError


    @classmethod
    def _init_config(cls):
        pass


    @classmethod
    def set_logger_queue(cls, logger_queue):
        cls.logger_queue = logger_queue
        if cls.config_logger:
            cls._assign_key_value(cls.config_logger, 'queue', logger_queue)


    @classmethod
    def _assign_key_value(cls, dic, target_key, new_value):
        for key, value in dic.items():
            if isinstance(value, dict):
                cls._assign_key_value(value, target_key, new_value)
            elif key == target_key:
                if value is None or value == 'None' or value == '' or isinstance(value, multiprocessing.queues.Queue):
                    dic[key] = new_value


    def __call__(self, logger_queue):
        self.set_logger_queue(self.__class__.logger_queue)
        return self
