from unittest.mock import patch, mock_open

import pytest

from test.tool import config_server_obj


@patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
@patch("os.path.join", lambda x, y: 'path/filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
@patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
@patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
class TestConfigMixinLogger:
    test_json = '{"host":"abc", "port":1234, "authkey":"xyz", "user_id": "pqr", "login": "uvw", "timeout":123, "keepalive":456, "retry":789}'
    EXPECTED = {"host": "abc", "port": 1234, "authkey": "xyz", "user_id": "pqr", "login": "uvw", "timeout": 123, "keepalive": 456, "retry": 789}


    def test_base(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj("tmp_server_name_base")
        assert some_config.config == self.EXPECTED
        assert some_config.get_config_dict() == self.EXPECTED
        assert some_config.host() == 'abc'
        assert some_config.port() == 1234
        assert some_config.authkey() == 'xyz'
        assert some_config.timeout() == 123
        assert some_config.keepalive() == 456
        assert some_config.retry() == 789
        assert some_config.server_name == 'tmp_server_name_base'


    def test__check_config(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj("tmp_server_name_cfg")
        assert some_config._check_config() == None

        # Port is int
        test_json_error_port = '{"host":"abc", "port":"1234", "authkey":"xyz", "timeout":"123", "keepalive":"456", "retry":"789"}'
        with patch("builtins.open", new_callable=mock_open, read_data=test_json_error_port):
            with pytest.raises(AttributeError) as ctx:
                config_server_obj('tmp_server_name_cfg2')
        assert ctx.errisinstance(AttributeError) and 'port' in ctx.exconly().lower()

        # Timeout is int
        test_json_error_timeout = '{"host":"abc", "port":1234, "authkey":"xyz", "timeout":"123", "keepalive":456, "retry":789}'
        with patch("builtins.open", new_callable=mock_open, read_data=test_json_error_timeout):
            with pytest.raises(AttributeError) as ctx:
                config_server_obj('tmp_server_name_cfg3')
        assert ctx.errisinstance(AttributeError) and 'timeout' in ctx.exconly().lower()

        # Keepalive is int
        test_json_error_keepalive = '{"host":"abc", "port":1234, "authkey":"xyz", "timeout":123, "keepalive":"456", "retry":789}'
        with patch("builtins.open", new_callable=mock_open, read_data=test_json_error_keepalive):
            with pytest.raises(AttributeError) as ctx:
                config_server_obj('tmp_server_name_cfg4')
        assert ctx.errisinstance(AttributeError) and 'keepalive' in ctx.exconly().lower()

        # retry is int
        test_json_error_retry = '{"host":"abc", "port":1234, "authkey":"xyz", "timeout":123, "keepalive":456, "retry":"789"}'
        with patch("builtins.open", new_callable=mock_open, read_data=test_json_error_retry):
            with pytest.raises(AttributeError) as ctx:
                config_server_obj('tmp_server_name_cfg5')
        assert ctx.errisinstance(AttributeError) and 'retry' in ctx.exconly().lower()


    def test_host(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg6')
        assert some_config.host() == 'abc'


    def test_port(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg7')
        assert some_config.port() == 1234


    def test_login(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg8')
        assert some_config.login() == 'uvw'


    def test_authkey(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj("tmp_server_name_cfg9")
        assert some_config.authkey() == 'xyz'


    def test_user_id(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj("tmp_server_name_cfg10")
        assert some_config.user_id() == 'pqr'


    def test_timeout(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg11')
        assert some_config.timeout() == 123


    def test_keepalive(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg12')
        assert some_config.keepalive() == 456


    def test_retry(self):
        with patch("builtins.open", new_callable=mock_open, read_data=self.test_json):
            some_config = config_server_obj('tmp_server_name_cfg13')
        assert some_config.retry() == 789


    # @classmethod
    # def _config_obj(cls, queue):
    #     class ConfigTest(ConfigMixInServer):
    # 
    #         def __init__(self, logger_queue):
    #             super().__init__(logger_queue)
    # 
    # 
    #     ConfigTest.__abstractmethods__ = frozenset()
    #     return ConfigTest(queue)
