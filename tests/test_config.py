import unittest
from unittest.mock import MagicMock, mock_open, patch

from src.conf import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        config = {
            'env': 'development',
            'apikey': '2b78f637972b1c9d',
            'store': 'http://simple.com',
            'theme_id': 1
        }
        self.config = Config(**config)

    @patch("yaml.load", autospec=True)
    @patch("os.path.exists", autospec=True)
    def test_read_config_file_with_config_file_should_be_read_data_correctly(self, mock_patch_exists, mock_load_yaml):
        mock_patch_exists.return_value = True
        mock_load_yaml.return_value = {
            'development': {
                'apikey': '2b78f637972b1c9d1234',
                'store': 'http://example.com',
                'theme_id': 1234
            }
        }
        with patch('builtins.open', mock_open(read_data='yaml data')):
            self.config.read_config()

        self.assertEqual(self.config.apikey, '2b78f637972b1c9d1234')
        self.assertEqual(self.config.store, 'http://example.com')
        self.assertEqual(self.config.theme_id, 1234)

    @patch("yaml.dump", autospec=True)
    @patch("yaml.load", autospec=True)
    @patch("os.path.exists", autospec=True)
    def test_write_config_file_without_config_file_should_write_data_correctly(
        self, mock_patch_exists, mock_load_yaml, mock_dump_yaml
    ):
        mock_patch_exists.return_value = True
        mock_dump_yaml.return_value = 'yaml data'
        mock_load_yaml.return_value = {
            'sandbox': {
                'apikey': '2b78f637972b1c9dabcd',
                'store': 'http://sandbox.com',
                'theme_id': 5678
            }
        }

        self.config.apikey = '2b78f637972b1c9d1234'
        self.config.store = 'http://example.com'
        self.config.theme_id = 1234

        config = {
            'sandbox': {
                'apikey': '2b78f637972b1c9dabcd',
                'store': 'http://sandbox.com',
                'theme_id': 5678
            },
            'development': {
                'apikey': '2b78f637972b1c9d1234',
                'store': 'http://example.com',
                'theme_id': 1234
            }
        }

        with patch('builtins.open', mock_open()):
            with open('config.yml') as f:
                self.config.write_config()
                mock_dump_yaml.assert_called_once_with(config, f)

    def test_validate_config_should_raise_expected_error(self):
        with self.assertRaises(TypeError) as error:
            self.config.apikey = None
            self.config.store = 'http://example.com'
            self.config.theme_id = 1234
            self.config.validate_config()
        self.assertEqual(str(error.exception), '[development] argument -a/--apikey is required.')

        with self.assertRaises(TypeError) as error:
            self.config.apikey = '2b78f637972b1c9d1234'
            self.config.store = None
            self.config.theme_id = 1234
            self.config.validate_config()
        self.assertEqual(str(error.exception), '[development] argument -s/--store is required.')

        with self.assertRaises(TypeError) as error:
            self.config.apikey = '2b78f637972b1c9d1234'
            self.config.store = 'http://example.com'
            self.config.theme_id = None
            self.config.validate_config()
        self.assertEqual(str(error.exception), '[development] argument -t/--theme_id is required.')

        self.config.apikey = None
        self.config.store = None
        self.config.theme_id = None

        with self.assertRaises(TypeError) as error:
            self.config.validate_config()
        self.assertEqual(str(error.exception),
                         '[development] argument -a/--apikey, -s/--store, -t/--theme_id are required.')

        with self.assertRaises(TypeError) as error:
            self.config.apikey_required = True
            self.config.store_required = True
            self.config.theme_id_required = False
            self.config.validate_config()
        self.assertEqual(str(error.exception), '[development] argument -a/--apikey, -s/--store are required.')

    def test_save_config_should_validate_and_write_config_correctly(self):
        with patch("src.conf.Config.write_config") as mock_write_config:
            with patch("src.conf.Config.validate_config") as mock_validate_config:
                self.config.save()
        mock_validate_config.assert_called_once()
        mock_write_config.assert_called_once()

        with patch("src.conf.Config.write_config") as mock_write_config:
            with patch("src.conf.Config.validate_config") as mock_validate_config:
                self.config.save(write_file=False)
        mock_validate_config.assert_called_once()
        mock_write_config.assert_not_called()

    def test_parser_config_should_set_config_config_correctly(self):
        config = {
            'env': 'sandbox',
            'apikey': '2b78f637972b1c9d1234',
            'store': 'http://sandbox.com',
            'theme_id': 1234
        }
        parser = MagicMock(**config)

        with patch("src.conf.Config.write_config") as mock_write_config:
            self.config.parser_config(parser=parser)

        self.assertEqual(self.config.apikey, '2b78f637972b1c9d1234')
        self.assertEqual(self.config.store, 'http://sandbox.com')
        self.assertEqual(self.config.theme_id, 1234)
        mock_write_config.assert_not_called()

        with patch("src.conf.Config.write_config") as mock_write_config:
            self.config.parser_config(parser=parser, write_file=True)

        self.assertEqual(self.config.apikey, '2b78f637972b1c9d1234')
        self.assertEqual(self.config.store, 'http://sandbox.com')
        self.assertEqual(self.config.theme_id, 1234)
        mock_write_config.assert_called_once()
