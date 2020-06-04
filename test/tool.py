import logging
from unittest.mock import patch, mock_open

from via_common.multiprocess.background_thread import BackgroundThread
from via_common.network.middleware import Middleware
from via_common.network.middleware_redis import MiddlewareRedis
from via_common.util.config_mixin import ConfigMixIn
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer


def config_obj():
    class ConfigTest(ConfigMixIn):
        pass


    ConfigTest.__abstractmethods__ = frozenset()
    return ConfigTest()


@patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
@patch("os.path.join", lambda x, y: 'path/filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
@patch('via_common.multiprocess.logger_manager.LoggerManager.set_child_logger_queue')
def config_server_obj(server_name='', _=None) -> ConfigMixInServer:
    # config_server = '{"host":"abc", "port":1234, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'


    class ConfigServerTest(ConfigMixInServer):

        def __init__(self, server_name):
            super().__init__(server_name)


    ConfigServerTest.__abstractmethods__ = frozenset()
    config_server = ConfigServerTest(server_name)
    return config_server


class ConfigServerPure(ConfigMixInServer):
    config_dict = None


    def __init__(self, config_dict, server_name):
        self.__class__.config_dict = config_dict
        super().__init__(server_name)


    def __call__(self):
        return self


    @classmethod
    def get_config_path(cls):
        return 'path'


    @classmethod
    def get_config_filename(cls):
        # Something like return os.getenv('CONFIG_FILENAME')
        return 'filename.json'


    @classmethod
    def _init_config(cls):
        cls.config = cls.config_dict


    @classmethod
    def _read_config(cls):
        return cls.config_dict


@patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
@patch("os.path.join", lambda x, y: 'path/filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
@patch('via_common.util.config_mixin_logger.ConfigMixInLogger._init_config_logger', lambda x, y: None)
def config_logger_obj(config_logger='{"subprocess":{}}', logger_queue=None) -> ConfigMixInLogger:
    class ConfigLoggerTest(ConfigMixInLogger):

        def __init__(self, logger_queue):
            super().__init__(logger_queue)


        def __call__(self):
            return self


    ConfigLoggerTest.__abstractmethods__ = frozenset()
    with patch("builtins.open", new_callable=mock_open, read_data=config_logger):
        ConfigLoggerTest.config = None
        ConfigLoggerTest.config_logger = None
        config_logger = ConfigLoggerTest(logger_queue)
    return config_logger


@patch('logging.config.dictConfig')
def middleware_redis_obj(config_server: ConfigMixInServer,
                         config_logger: ConfigMixInLogger,
                         logger_queue, _):
    class MiddlewareTest(MiddlewareRedis):

        def __init__(self, config_server: ConfigMixInServer,
                     config_logger: ConfigMixInLogger,
                     logger_queue=None):
            super().__init__(config_server, config_logger, logger_queue)


    MiddlewareTest.__abstractmethods__ = frozenset()
    return MiddlewareTest(config_server, config_logger, logger_queue)


def middleware_obj(config):
    class MiddlewareTest(Middleware):

        def __init__(self, config_server: ConfigMixInServer):
            super().__init__(config_server)


    MiddlewareTest.__abstractmethods__ = frozenset()
    return MiddlewareTest(config)


class ConnectRaised(Exception):
    pass


def backgroundthread_obj(config_internal_conn, middleware):
    class BackgroundThreadTest(BackgroundThread):

        def __init__(self, config_internal_conn: ConfigMixInServer, middleware: Middleware):
            super().__init__(config_internal_conn, middleware)
            self.called_shutdown = False


        def _initialise_thread_logger(self):
            self.logger = logging.getLogger(__name__)


        def shutdown(self):
            self.called_shutdown = True


    BackgroundThreadTest.__abstractmethods__ = frozenset()
    return BackgroundThreadTest(config_internal_conn, middleware)
