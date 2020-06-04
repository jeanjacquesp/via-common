from unittest.mock import patch, mock_open

import pytest

from test.tool import config_server_obj, middleware_obj


class TestMiddleware:

    @pytest.fixture(scope="class")
    def setup(self):
        config_server = '{"host":"abc", "port":1234, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'
        with patch("builtins.open", new_callable=mock_open, read_data=config_server):
            self.__class__.config_server = config_server_obj()
        self.__class__.middleware = middleware_obj(self.config_server)


    def test__init__(self, setup):
        assert self.middleware.config == self.config_server
        assert self.middleware.host == self.config_server.host()
        assert self.middleware.port == self.config_server.port()
        assert self.middleware.password == self.config_server.authkey()


    def test_connect(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.middleware.connect()
        assert isinstance(ctx.value, NotImplementedError)


    def test_shutdown(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.middleware.shutdown()
        assert isinstance(ctx.value, NotImplementedError)


    def test_publish(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.middleware.publish('channel', 'message')
        assert isinstance(ctx.value, NotImplementedError)


    def test_subscribe_one_forever(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.middleware.subscribe_one_forever('channel', None)
        assert isinstance(ctx.value, NotImplementedError)


    def test__check_conn(self, setup):
        with pytest.raises(NotImplementedError) as ctx:
            self.middleware._check_conn()
        assert isinstance(ctx.value, NotImplementedError)

    # @classmethod
    # def _middleware_obj(cls, config):
    #     class MiddlewareTest(Middleware):
    #
    #         def __init__(self, config_server: ConfigMixInServer):
    #             super().__init__(config_server)
    #
    #
    #     MiddlewareTest.__abstractmethods__ = frozenset()
    #     return MiddlewareTest(config)


    # @classmethod
    # @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    # @patch("os.path.join", lambda x, y: 'path/filename.json')
    # @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    # @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    # @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    # def _config_server_obj(cls):
    #     class ConfigServerTest(ConfigMixInServer):
    #
    #         def __init__(self, server_name):
    #             super().__init__(server_name)
    #
    #
    #     config_server = '{"host":"abc", "port":1234, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'
    #     ConfigServerTest.__abstractmethods__ = frozenset()
    #     with patch("builtins.open", new_callable=mock_open, read_data=config_server):
    #         config_server = ConfigServerTest('queue')
    #     return config_server
