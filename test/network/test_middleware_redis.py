from unittest.mock import patch, mock_open

import pytest

from test.tool import middleware_redis_obj, config_server_obj, config_logger_obj
from via_common.multiprocess.logger_manager import LoggerManager
from via_common.multiprocess.pipe_adapter import SIGNAL_SHUTDOWN_START


mocked_queue = {}


def mocked_lpush(channel, message):
    global mocked_queue
    val = []
    if hasattr(mocked_queue, channel):
        val = mocked_queue.get(channel)
    val.append(message)
    mocked_queue.update({channel: val})


class PingFailed(Exception):
    pass


class TestMiddlewareRedis:
    config_server = None
    config_logger = None
    middleware = None


    @pytest.fixture(scope="class")
    def setup(self):
        with patch("via_common.multiprocess.logger_manager.LoggerManager._check_or_create_directory"):
            # with patch("via_common.multiprocess.logger_manager.LoggerManager.config_logger", lambda: '{"root":{"version":1}, "subprocess":{}}'):
            LoggerManager().__del__()
            config_logger = config_logger_obj(config_logger='{"root":{"version":1}, "subprocess":{}}')
            LoggerManager.init_root_logger(config_logger)
            # patching manually the LoggerManager to avoid some side effects that are NOT under the scope of what is tested here
            LoggerManager.logger_queue_listener = 'not none'
            config_server = '{"host":"abc", "port":1234, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'
            with patch("builtins.open", new_callable=mock_open, read_data=config_server):
                self.__class__.config_server = config_server_obj()
            config_logger = config_logger_obj(config_logger='{"root":{"version":1}, "subprocess":{}}')
            self.__class__.middleware = middleware_redis_obj(self.config_server,
                                                             config_logger,
                                                             'queue')
            yield "teardown"
            LoggerManager().__del__()


    def test__init__(self, setup):
        assert self.middleware.config == self.config_server
        assert self.middleware.host == self.config_server.host()
        assert self.middleware.port == self.config_server.port()
        assert self.middleware.password == self.config_server.authkey()


    @patch('redis.StrictRedis', side_effect=['redis'])
    @patch('redis.StrictRedis.ping', side_effect=['redis'])
    def test_connect(self, setup, _):
        self.middleware.connect()
        assert self.middleware.connected


    @patch("redis.StrictRedis", side_effect=['redis'])
    @patch("redis.StrictRedis.ping", side_effect=PingFailed)
    def test_connect_error(self, setup, _):
        with pytest.raises(ConnectionError) as ctx:
            self.middleware.connect()
        assert isinstance(ctx.value, ConnectionError)


    @patch("redis.StrictRedis.ping", side_effect=ConnectionError)
    def test_connect_error_unknown(self, setup):
        with pytest.raises(ConnectionError) as ctx:
            self.middleware.connect()
        assert isinstance(ctx.value, ConnectionError)


    def test_register_shutdown_channel(self, setup):
        self.middleware.register_shutdown_channel('some_specific_channel')
        assert self.middleware.registered_channel == ['some_specific_channel']


    @patch('redis.StrictRedis.lpush', lambda _, channel, message: mocked_lpush(channel, message))
    def test_shutdown(self, setup):
        global mocked_queue
        mocked_queue = {}
        self.middleware.register_shutdown_channel('some_specific_channel2')
        assert not self.middleware.disconnecting
        self.middleware.shutdown()
        assert mocked_queue['some_specific_channel2'][0] == SIGNAL_SHUTDOWN_START
        assert self.middleware.disconnecting


    @patch('redis.StrictRedis', side_effect=['redis'])
    @patch('redis.StrictRedis.ping', side_effect=['redis'])
    @patch('redis.StrictRedis.lpush')
    def test_publish(self, setup, _, __):
        self.middleware.connect()
        self.middleware.publish('channel', 'message')


    @patch('redis.StrictRedis.brpoplpush')
    @patch('redis.StrictRedis.lrem', side_effect=InterruptedError)
    def test_subscribe_one_forever(self, setup, _):
        with pytest.raises(InterruptedError) as ctx:
            self.middleware.subscribe_one_forever('channel', None)
        assert isinstance(ctx.value, InterruptedError)


    @patch('redis.StrictRedis.ping')
    def test__check_conn(self, setup):
        self.middleware._check_conn()
