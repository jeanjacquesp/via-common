import logging
import multiprocessing
import multiprocessing.queues
from functools import partial
from multiprocessing.managers import BaseProxy
from unittest.mock import patch

import pytest

from test.tool import ConfigServerPure, config_logger_obj
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.process_mixin import ProcessMixin
from via_common.multiprocess.queue_manager import QueueManager
from via_common.util.config_mixin_logger import ConfigMixInLogger
from via_common.util.config_mixin_server import ConfigMixInServer


process_started = False
process_joined = False
process_closed = False
pipe_started = False
run_child_forever = False


def process_start_called():
    global process_started
    process_started = True


def process_join_called():
    global process_joined
    process_joined = True


def process_close_called():
    global process_closed
    process_closed = True


def process_pipe_start_called():
    global pipe_started
    pipe_started = True


def process_run_child_forever_called(logger_queue):
    global run_child_forever
    if isinstance(logger_queue, BaseProxy):
        run_child_forever = True
    else:
        raise RuntimeError('the logger_queue is not a queue')


class TestProcessMixIn:
    config_conn_dict = None
    config_internal_conn = None
    config_logger = None
    process = None
    queue_manager = None


    @pytest.fixture(scope='class')
    def setup(self):
        with patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory"):
            self.__class__.config_conn_dict = {"host": "127.0.0.1", "port": 41570, "authkey": "abc"}
            LoggerManager().__del__()
            self.__class__.config_internal_conn = ConfigServerPure(self.config_conn_dict, 'test')
            self.__class__.config_logger = config_logger_obj(config_logger='{"root":{"version":1}, "subprocess":{"version":1}}')
            queue_name_list = ['test']
            shutdown_receiver = None
            self.__class__.process = self._processmixin_obj('process_name', self.config_internal_conn, self.config_logger, queue_name_list, shutdown_receiver)
            LoggerManager.init_root_logger(self.config_logger)
            self.__class__.queue_manager = QueueManager(self.config_internal_conn, ['test'])
        yield "teardown"
        LoggerManager().__del__()


    def test_shutdown(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.process.shutdown()
        assert ctx.errisinstance(NotImplementedError)


    def test__initialise_child_logger(self, setup):
        self.process._initialise_child_logger()
        assert self.process.logger is not None


    def test__run_child_forever(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.process._run_child_forever()
        assert ctx.errisinstance(NotImplementedError)


    @patch("multiprocessing.process.BaseProcess.start", lambda _: process_start_called())
    def test_start(self, setup):
        global process_started
        self.process.start()
        assert process_started


    @patch("multiprocessing.process.BaseProcess.join", lambda _: process_join_called())
    def test_join(self, setup):
        global process_joined
        self.process.join()
        assert process_joined


    @patch("multiprocessing.process.BaseProcess.close", lambda _: process_close_called())
    def test_close(self, setup):
        global process_closed
        self.process.close()
        assert process_closed


    def test_get_process(self, setup):
        process = self.process.get_process()
        assert isinstance(process, multiprocessing.process.BaseProcess)


    @patch("via_common.multiprocess.pipe_adapter.PipeAdapter.start", lambda _: process_pipe_start_called())
    @patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory")
    @patch("via_common.multiprocess.process_mixin.ProcessMixin._run_child_forever", lambda _, logger_queue: process_run_child_forever_called(logger_queue))
    def test__run_child_process(self, setup):
        global run_child_forever
        self.process._run_child_process(partial(self.config_internal_conn), partial(self.config_logger))
        assert isinstance(self.process.test, multiprocessing.managers.BaseProxy)
        assert isinstance(self.process.system_queue, multiprocessing.managers.BaseProxy)
        assert self.process.logger is not None
        assert run_child_forever


    @classmethod
    def _processmixin_obj(cls, process_name, config_internal_conn: ConfigMixInServer, config_logger: ConfigMixInLogger, queue_name_list, shutdown_receiver):
        class ProcessMixinTest(ProcessMixin):

            def __init__(self, process_name, config_internal_conn, config_logger, queue_name_list, shutdown_receiver):
                super().__init__(process_name, config_internal_conn, config_logger, queue_name_list, shutdown_receiver)


            def _initialise_child_logger(self):
                self.logger = logging.getLogger(__name__)


        ProcessMixinTest.__abstractmethods__ = frozenset()
        return ProcessMixinTest(process_name, config_internal_conn, config_logger, queue_name_list, shutdown_receiver)
