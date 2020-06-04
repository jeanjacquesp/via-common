#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from abc import ABCMeta
from abc import abstractmethod

from via_common.util.config_mixin_server import ConfigMixInServer


class Middleware(metaclass=ABCMeta):
    """
    A helper class to define the interfaces for connecting to the middleware
    """


    def __init__(self, config: ConfigMixInServer):
        self.config = config
        self.host = config.host()
        self.port = config.port()
        self.password = config.authkey()


    @abstractmethod
    def connect(self):
        raise NotImplementedError


    @abstractmethod
    def shutdown(self):
        raise NotImplementedError


    @abstractmethod
    def publish(self, channel, message):
        raise NotImplementedError


    @abstractmethod
    def subscribe_one_forever(self, channel: str, callback_handle_message):
        raise NotImplementedError


    @abstractmethod
    def _check_conn(self):
        raise NotImplementedError
