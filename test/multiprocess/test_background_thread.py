import multiprocessing
import multiprocessing.queues
from unittest.mock import patch, mock_open

import pytest

from test.tool import config_server_obj, middleware_obj, backgroundthread_obj, config_logger_obj, ConfigServerPure, ConnectRaised
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.pipe_adapter import SIGNAL_SHUTDOWN_START
from via_common.multiprocess.queue_manager import QueueManager


class SomeException(Exception):
    pass


class TestBackgroundThread:
    config_internal_conn = None
    middleware = None
    backgroundthread = None
    queue_manager = None


    @pytest.fixture(scope="class")
    def setup(self):
        with patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory"):
            LoggerManager().__del__()
            config_logger = config_logger_obj(config_logger='{"root":{"version":1}, "subprocess":{}}')
            LoggerManager.init_root_logger(config_logger)
            config_conn = {"host": "127.0.0.1", "port": 41567, "authkey": "abc"}
            # We need a proper config otherwise cannot be pickled
            self.__class__.config_internal_conn = ConfigServerPure(config_conn, 'test')
            config_server = '{"host":"127.0.0.1", "port":12346, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'
            with patch("builtins.open", new_callable=mock_open, read_data=config_server):
                self.__class__.config_server = config_server_obj()
            self.__class__.middleware = middleware_obj(self.config_server)
            self.__class__.queue_manager = QueueManager(self.config_internal_conn)
            self.__class__.backgroundthread = backgroundthread_obj(self.config_internal_conn, self.middleware)
        yield "teardown"
        LoggerManager().__del__()


    def test_shutdown(self, setup):
        self.backgroundthread.shutdown()
        assert self.backgroundthread.called_shutdown


    def test__initialise_thread_logger(self, setup):
        self.backgroundthread._initialise_thread_logger()
        assert self.backgroundthread.logger is not None


    @patch("via_common.network.middleware.Middleware.connect")
    def test__start_background_async(self, setup2):
        self.backgroundthread._start_background_async(lambda x: x, 'X')
        self.backgroundthread.system_queue.put(SIGNAL_SHUTDOWN_START)
        assert self.backgroundthread.called_shutdown


    @patch("via_common.network.middleware.Middleware.connect", side_effect=ConnectRaised)
    def test__run_thread_forever(self, setup):
        with pytest.raises(ConnectRaised) as ctx:
            self.backgroundthread._run_thread_forever(lambda x: x, 'X')
        assert isinstance(ctx.value, ConnectRaised)


    def test__setup_system_queue(self, setup):
        self.backgroundthread._setup_system_queue()
        assert isinstance(self.backgroundthread.system_queue, multiprocessing.managers.BaseProxy)


    @patch("multiprocessing.managers.BaseManager.connect", side_effect=ConnectRaised)
    def test__setup_system_queue_error(self, setup):
        with pytest.raises(ConnectionError) as ctx:
            self.backgroundthread._setup_system_queue()
        assert isinstance(ctx.value, ConnectionError)
