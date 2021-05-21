import os
import unittest
from unittest.mock import call, MagicMock, mock_open, patch

from src.utils import _validate_config, create_and_get_config, get_config


class TestUtils(unittest.TestCase):
    def setUp(self):
        self.mock_file = mock_open(
            read_data='development:\n  apikey: 2b78f637972b1c9d\n  store: http://development.com\n  theme_id: "1"\n'
                      'sandbox:\n  apikey: 2b78f637972b1c9d\n  store: http://sandbox.com\n  theme_id: "5"\n'
        )
        self.config_file = os.path.join(os.getcwd(), 'config.yml')

    #####
    # _validate_config
    #####
    def test_validate_config_should_raise_expected_error(self):
        with self.assertRaises(TypeError):
            _validate_config('env', None, '1', 'http://simple.com')

        with self.assertRaises(TypeError):
            _validate_config('env', 'apikey', None, 'http://simple.com')

        with self.assertRaises(TypeError):
            _validate_config('env', 'apikey', '1', None)

    #####
    # get_config
    #####
    @patch('src.utils.os.path.exists', autospec=True)
    def test_get_config_with_file_not_exist_and_parser_argument_is_none_should_raise_error(
        self, mocker_path_exists
    ):
        mocker_path_exists.return_value = False
        parser = MagicMock(env=None, apikey=None, theme_id=None, store=None)

        with self.assertRaises(TypeError):
            get_config(parser)

    @patch('src.utils.os.path.exists', autospec=True)
    def test_get_config_with_file_not_exist_and_parser_argument_is_not_none_should_return_config_belong_to_parser(
        self, mocker_path_exists
    ):
        mocker_path_exists.return_value = False
        parser = MagicMock(env='development', apikey='apikey', theme_id='1', store='http://simple.com')

        config_info = get_config(parser)

        self.assertEqual(config_info.env, 'development')
        self.assertEqual(config_info.apikey, 'apikey')
        self.assertEqual(config_info.theme_id, '1')
        self.assertEqual(config_info.store, 'http://simple.com')

    @patch('src.utils.os.path.exists', autospec=True)
    def test_get_config_with_file_exists_and_parser_argument_is_none_should_get_config_info_from_file(
        self, mocker_path_exists
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='development', apikey=None, theme_id=None, store=None)

        with patch('builtins.open', self.mock_file):
            config_info = get_config(parser)

            self.assertEqual(config_info.env, 'development')
            self.assertEqual(config_info.apikey, '2b78f637972b1c9d')
            self.assertEqual(config_info.theme_id, '1')
            self.assertEqual(config_info.store, 'http://development.com')

            expected_calls = [
                call(self.config_file, 'r')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

    @patch('src.utils.os.path.exists', autospec=True)
    def test_get_config_with_file_exists_and_parser_argument_is_not_none_should_return_config_belong_to_parser(
        self, mocker_path_exists
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='development', apikey='apikey', theme_id='10', store=None)

        with patch('builtins.open', self.mock_file):
            config_info = get_config(parser)

            self.assertEqual(config_info.env, 'development')
            self.assertEqual(config_info.apikey, 'apikey')
            self.assertEqual(config_info.theme_id, '10')
            self.assertEqual(config_info.store, 'http://development.com')

            expected_calls = [
                call(self.config_file, 'r')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

    @patch('src.utils.yaml.dump', autospec=True)
    @patch('src.utils.os.path.exists', autospec=True)
    def test_get_config_with_file_exists_and_parser_is_not_none_and_write_file_should_write_file_and_return_config(
        self, mocker_path_exists, mock_yaml_dump
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='development', apikey='apikey_value', theme_id='10', store=None)

        with patch('builtins.open', self.mock_file):
            config_info = get_config(parser, write_file=True)

            self.assertEqual(config_info.env, 'development')
            self.assertEqual(config_info.apikey, 'apikey_value')
            self.assertEqual(config_info.theme_id, '10')
            self.assertEqual(config_info.store, 'http://development.com')

            expected_calls = [
                call(self.config_file, 'r'),
                call(self.config_file, 'w')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

            # write file with expected config
            expected_configs = {
                'development': {'apikey': 'apikey_value', 'store': 'http://development.com', 'theme_id': '10'},
                'sandbox': {'apikey': '2b78f637972b1c9d', 'store': 'http://sandbox.com', 'theme_id': '5'}
            }
            self.assertEqual(expected_configs, mock_yaml_dump.call_args.args[0])

    #####
    # create_and_get_config
    #####
    @patch('builtins.open', autospec=True)
    @patch('src.utils.yaml.dump', autospec=True)
    @patch('src.utils.os.path.exists', autospec=True)
    def test_create_and_get_config_with_config_file_not_exist_should_create_file_and_return_expected_config(
        self, mocker_path_exists, mock_yaml_dump, mock_open_file
    ):
        mocker_path_exists.return_value = False
        parser = MagicMock(env='new_env', apikey='aasdasdqwqeew', theme_id='1', store='http://newenv.com')

        config = create_and_get_config(parser)

        self.assertEqual(config.env, 'new_env')
        self.assertEqual(config.apikey, 'aasdasdqwqeew')
        self.assertEqual(config.theme_id, '1')
        self.assertEqual(config.store, 'http://newenv.com')

        # write file with expected config
        expected_configs = {
            'new_env': {'apikey': 'aasdasdqwqeew', 'store': 'http://newenv.com', 'theme_id': '1'}
        }
        self.assertEqual(expected_configs, mock_yaml_dump.call_args.args[0])

        expected_calls = [
            call(self.config_file, 'w')
        ]
        self.assertEqual(mock_open_file.call_args_list, expected_calls)

    @patch('src.utils.os.path.exists', autospec=True)
    def test_create_and_get_config_with_file_exists_and_parser_argument_is_none_should_read_and_get_config_from_file(
        self, mocker_path_exists
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='sandbox', apikey=None, theme_id=None, store=None)

        with patch('builtins.open', self.mock_file):
            config_info = create_and_get_config(parser)

            self.assertEqual(config_info.env, 'sandbox')
            self.assertEqual(config_info.apikey, '2b78f637972b1c9d')
            self.assertEqual(config_info.theme_id, '5')
            self.assertEqual(config_info.store, 'http://sandbox.com')

            expected_calls = [
                call(self.config_file, 'r')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

    @patch('src.utils.yaml.dump', autospec=True)
    @patch('src.utils.os.path.exists', autospec=True)
    def test_create_and_get_config_with_file_exists_and_parser_is_not_none_should_write_file_and_update_config(
        self, mocker_path_exists, mock_yaml_dump
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='sandbox', apikey='apikey', theme_id='3', store='http://sandbox2.com')

        with patch('builtins.open', self.mock_file):
            config_info = create_and_get_config(parser)

            self.assertEqual(config_info.env, 'sandbox')
            self.assertEqual(config_info.apikey, 'apikey')
            self.assertEqual(config_info.theme_id, '3')
            self.assertEqual(config_info.store, 'http://sandbox2.com')

            expected_calls = [
                call(self.config_file, 'r'),
                call(self.config_file, 'w')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

            # write file with expected config
            expected_configs = {
                'development': {'apikey': '2b78f637972b1c9d', 'store': 'http://development.com', 'theme_id': '1'},
                'sandbox': {'apikey': 'apikey', 'store': 'http://sandbox2.com', 'theme_id': '3'}
            }
            self.assertEqual(expected_configs, mock_yaml_dump.call_args.args[0])

    @patch('src.utils.yaml.dump', autospec=True)
    @patch('src.utils.os.path.exists', autospec=True)
    def test_create_and_get_config_with_file_exists_and_new_env_parser_should_write_file_and_update_config(
        self, mocker_path_exists, mock_yaml_dump
    ):
        mocker_path_exists.return_value = True
        parser = MagicMock(env='production', apikey='apikey_production', theme_id='3', store='http://production.com')

        with patch('builtins.open', self.mock_file):
            config_info = create_and_get_config(parser)

            self.assertEqual(config_info.env, 'production')
            self.assertEqual(config_info.apikey, 'apikey_production')
            self.assertEqual(config_info.theme_id, '3')
            self.assertEqual(config_info.store, 'http://production.com')

            expected_calls = [
                call(self.config_file, 'r'),
                call(self.config_file, 'w')
            ]
            self.assertEqual(self.mock_file.call_args_list, expected_calls)

            # write file with expected config
            expected_configs = {
                'development': {'apikey': '2b78f637972b1c9d', 'store': 'http://development.com', 'theme_id': '1'},
                'sandbox': {'apikey': '2b78f637972b1c9d', 'store': 'http://sandbox.com', 'theme_id': '5'},
                'production': {'apikey': 'apikey_production', 'theme_id': '3', 'store': 'http://production.com'}
            }
            self.assertEqual(expected_configs, mock_yaml_dump.call_args.args[0])
