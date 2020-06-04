import logging
import multiprocessing
import multiprocessing.queues
import os
from unittest.mock import patch

import pytest

from test.tool import config_logger_obj, ConfigServerPure
from via_common.multiprocess.logger_manager import LoggerManager, SimpleHandler
from via_common.util.helper import dict2obj


basic_logger_config = """
{
  "root": {
    "version": 1,
    "formatters": {
    },
    "handlers": {
      "file": {
        "class": "logging.FileHandler",
        "mode": "w",
        "filename": "logger_file_name"
      },
      "errors": {
        "class": "logging.FileHandler",
        "filename": "logger_file_name_error",
        "mode": "w"
      }
    },
    "root": {
      "level": "DEBUG",
      "handlers": [
        "file",
        "errors"
      ]
    }
  },
  "subprocess": {
    "version": 1,
    "handlers": {
      "queue": {
        "class": "logging.handlers.QueueHandler",
        "queue": "None"
      }
    },
    "root": {
      "handlers": [
        "queue"
      ]
    }
  }
}"""

logger_handled = False
makedirs_called = False


def simplehandler_handle_called(record):
    global logger_handled
    if record.name == 'test':
        logger_handled = True
    else:
        raise RuntimeError('SimpleHandler.handle was not called on the input record')


def loggermanager_makedirs_called(x):
    global makedirs_called
    if x == 'tmp_dirname':
        makedirs_called = True
    else:
        raise RuntimeError('LoggerManager did not create the log directory')


class TestLoggerManager:
    config_internal_conn = None
    queue_manager = None
    queue_name_list = None
    config_logger = None


    @pytest.fixture(scope="class")
    def setup(self):
        LoggerManager().__del__()
        config_conn = {"host": "127.0.0.1", "port": 41568, "authkey": "abc"}
        self.__class__.config_internal_conn = ConfigServerPure(config_conn, 'test')
        self.__class__.queue_name_list = ['test']
        self.__class__.config_logger = config_logger_obj(config_logger=basic_logger_config)
        yield "teardown"
        LoggerManager().__del__()
        logging.shutdown()
        import time
        time.sleep(1)
        if os.path.isfile('logger_file_name'):
            os.remove('logger_file_name')
        if os.path.isfile('logger_file_name_error'):
            os.remove('logger_file_name_error')


    #
    # Init root logger must be run first
    #
    def test_1_init_root_logger(self, setup):
        LoggerManager.init_root_logger(self.config_logger)
        assert isinstance(LoggerManager.logger_queue, multiprocessing.queues.Queue)
        assert LoggerManager.config_logger['subprocess']['handlers']['queue']['queue'] == LoggerManager.logger_queue


    @patch("logging.Logger.handle", lambda x, record: simplehandler_handle_called(record))
    def test_handle(self, setup):
        record = {'name': 'test'}
        record = dict2obj(record)
        simple = SimpleHandler()
        simple.handle(record)
        assert logger_handled


    def test_set_child_logger_queue(self, setup):
        new_logger_queue = multiprocessing.Queue()
        LoggerManager.set_child_logger_queue(self.config_logger, new_logger_queue)
        assert LoggerManager.logger_queue == new_logger_queue
        assert LoggerManager.config_logger['subprocess']['handlers']['queue']['queue'] == new_logger_queue


    def test_get_logger_queue(self, setup):
        assert LoggerManager.get_logger_queue() == LoggerManager.logger_queue


    @patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory")
    def test_get_logger(self, setup):
        logger = LoggerManager.get_logger('test')
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test'
        assert isinstance(LoggerManager.logger_queue_listener, logging.handlers.QueueListener)
        assert LoggerManager.logger_queue_listener.queue == LoggerManager.logger_queue


    @patch("os.path.exists", lambda x: False)
    @patch("os.path.dirname", lambda x: 'tmp_dirname')
    @patch("os.makedirs", lambda x: loggermanager_makedirs_called(x))
    def test__check_or_create_directory(self, setup):
        global makedirs_called
        LoggerManager._check_or_create_directory()
        assert makedirs_called
