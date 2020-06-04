import json
from unittest.mock import patch, mock_open

import pytest

from test.tool import config_obj


class TestConfigMixIn:

    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_base(self):
        test_json = '{"test":1}'
        with patch("builtins.open", new_callable=mock_open, read_data=test_json):
            some_config = config_obj()
        assert some_config.config == {'test': 1}
        assert some_config.get_config_dict() == {'test': 1}


    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_config_file_not_found(self):
        test_json = '{"test":1}'
        with pytest.raises(FileNotFoundError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                with patch("os.path.isfile", lambda x: False):
                    config_obj()
        assert ctx.errisinstance(FileNotFoundError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_json_error(self):
        test_json_error = '{"test:1}'
        with pytest.raises(json.JSONDecodeError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json_error):
                config_obj()
        assert ctx.errisinstance(json.JSONDecodeError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_get_config_path_not_implemented(self):
        test_json = '{"test":1}'
        with pytest.raises(NotImplementedError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                config_obj()
        assert ctx.errisinstance(NotImplementedError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_get_config_filename_not_implemented(self):
        test_json = '{"test":1}'
        with pytest.raises(NotImplementedError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                config_obj()
        assert ctx.errisinstance(NotImplementedError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    def test_init_config_not_implemented(self):
        test_json = '{"test":1}'
        with pytest.raises(NotImplementedError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                config_obj()
        assert isinstance(ctx.value, NotImplementedError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_wrong_data_type(self):
        test_json = 0xdeadbeef
        with pytest.raises(TypeError) as ctx:
            with patch("builtins.open", new_callable=mock_open, read_data=test_json):
                config_obj()
        assert ctx.errisinstance(TypeError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: None)
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: 'filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_missing_config_path(self):
        with pytest.raises(AttributeError) as ctx:
            with patch("builtins.open", lambda x: x):
                config_obj()
        assert ctx.errisinstance(AttributeError)


    @patch("os.path.isfile", lambda x: True if x == 'path/filename.json' else False)
    @patch("os.path.join", lambda x, y: 'path/filename.json')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_path', lambda: 'path')
    @patch('via_common.util.config_mixin.ConfigMixIn.get_config_filename', lambda: None)
    @patch('via_common.util.config_mixin.ConfigMixIn._init_config', lambda x: None)
    def test_missing_config_filename(self):
        with pytest.raises(AttributeError) as ctx:
            with patch("builtins.open", lambda x: x):
                config_obj()
        assert ctx.errisinstance(AttributeError)
