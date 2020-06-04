from unittest.mock import patch, mock_open

import pytest

from test.tool import config_logger_obj


class TestConfigMixInLogger:

    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    @patch('via_common.util.config_mixin_logger.ConfigMixInLogger._init_config_logger', lambda x, y: None)
    def test_base(self):
        test_json = '{"Inner":{"queue":""}}'
        EXPECTED = {"Inner": {"queue": "some_queue"}}
        with patch("builtins.open", new_callable=mock_open, read_data=test_json):
            some_config = config_logger_obj(test_json, "some_queue")
        assert some_config.config == EXPECTED
        assert some_config.config_logger == EXPECTED
        assert some_config.get_config_dict() == EXPECTED


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_init_config_logger_not_implemented(self):
        test_json = '{"Inner":{"queue":""}}'
        with pytest.raises(NotImplementedError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                config_logger_obj(test_json, 'some_queue')._init_config_logger(None)
        assert ctx.errisinstance(NotImplementedError)
