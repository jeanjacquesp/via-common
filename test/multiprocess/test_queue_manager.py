import multiprocessing
import multiprocessing.queues
from unittest.mock import patch

import pytest

from test.tool import ConfigServerPure, config_logger_obj
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.queue_manager import QueueManager


class TestQueueMananer:
    config_internal_conn = None
    queue_name_list = None
    queue_manager = None


    @pytest.fixture(scope="class")
    def setup(self):
        with patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory"):
            LoggerManager().__del__()
            config_logger = config_logger_obj(config_logger='{"root":{"version":1}, '
                                                            '"subprocess":{"version":1,'
                                                            '    "handlers":{"queue":{"class":"logging.handlers.QueueHandler","queue": "None"}}}}')
            LoggerManager.init_root_logger(config_logger)
            config_conn = {"host": "127.0.0.1", "port": 41569, "authkey": "abc"}
            # We need a proper config otherwise cannot be pickled
            self.__class__.config_internal_conn = ConfigServerPure(config_conn, 'test')
            self.__class__.queue_name_list = ['test']
            self.__class__.queue_manager = QueueManager(self.config_internal_conn, self.queue_name_list)
        yield "teardown"
        LoggerManager().__del__()


    def test_get_system_queue(self, setup):
        system_queue = self.queue_manager.get_system_queue()
        assert isinstance(system_queue, multiprocessing.queues.Queue)
        assert self.queue_manager.system_queue == system_queue


    def test_get_logger_queue(self, setup):
        logger_queue = self.queue_manager.get_logger_queue()
        assert isinstance(logger_queue, multiprocessing.queues.Queue)
        assert self.queue_manager.logger_queue == logger_queue
        assert LoggerManager.get_logger_queue() == logger_queue


    def test_get_queue_by_name(self, setup):
        test_queue = self.queue_manager.get_queue_by_name('test')
        assert isinstance(test_queue, multiprocessing.queues.Queue)


    def test__init_queue(self, setup):
        self.config_internal_conn.config['port'] += 10
        self.queue_manager._init_queue()
        assert self.queue_manager.manager._state.value == multiprocessing.managers.State.STARTED


    @patch("multiprocessing.managers.BaseManager.register", side_effect=EOFError)
    def test__init_queue_register_error(self, setup):
        with pytest.raises(ConnectionError) as ctx:
            self.config_internal_conn.config['port'] += 10
            self.queue_manager._init_queue()
        assert isinstance(ctx.value, ConnectionError)
