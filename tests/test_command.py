import os
import unittest
from unittest.mock import call, MagicMock, mock_open, patch

from watchgod.watcher import Change

from src.command import Command


class TestCommand(unittest.TestCase):
    def setUp(self):
        config = {
            'env': 'development',
            'apikey': '2b78f637972b1c9d',
            'theme_id': 1,
            'store': 'http://simple.com'
        }
        self.parser = MagicMock(**config)
        self.command = Command()

        self.mock_file = mock_open(read_data='{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>')

    #####
    # init
    #####
    def test_init_command_without_config_file_should_be_required_name_api_key_store_theme_id(self):
        with self.assertRaises(TypeError) as error:
            self.parser.name = None
            self.parser.apikey = None
            self.parser.store = None
            self.parser.theme_id = None
            self.command.init(self.parser)
        self.assertEqual(str(error.exception), '[development] argument -a/--apikey, -s/--store are required.')

    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_init_command_with_name_and_configs_should_be_call_create_theme_and_save_config(
        self, mock_write_config, mock_gateway
    ):
        mock_gateway.return_value.create_theme.return_value.json.return_value = {
            'id': 1234,
            'name': 'Test Init Theme',
            'active': False
        }
        with self.assertLogs(level='INFO') as cm:
            self.parser.name = 'Test Init Theme'
            self.parser.theme_id = None
            self.command.init(self.parser)

            expected_gateway_calls = [
                call(apikey='2b78f637972b1c9d', store='http://simple.com'),
                call().create_theme({'name': 'Test Init Theme'}),
                call().create_theme().json()
            ]

            self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        expected_logging = ['INFO:root:[development] Theme [1234] "Test Init Theme" has been created successfully.']
        self.assertEqual(cm.output, expected_logging)

        mock_write_config.assert_called_once()

    #####
    # list
    #####
    def test_list_command_without_config_file_should_be_required_api_key_store(self):
        with self.assertRaises(TypeError) as error:
            self.parser.apikey = None
            self.parser.store = None
            self.parser.theme_id = None
            self.command.list(self.parser)
        self.assertEqual(str(error.exception), '[development] argument -a/--apikey, -s/--store are required.')

    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_list_command_with_configs_should_be_show_theme_id_and_theme_name(
        self, mock_write_config, mock_gateway
    ):
        mock_gateway.return_value.get_themes.return_value.json.return_value = {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    'id': 1234,
                    'name': 'Default Theme',
                    'active': True
                },
                {
                    'id': 1235,
                    'name': 'Test Init Theme',
                    'active': False
                }
            ]
        }
        with self.assertLogs(level='INFO') as cm:
            self.command.list(self.parser)
            expected_gateway_calls = [
                call(store='http://simple.com', apikey='2b78f637972b1c9d'),
                call().get_themes(),
                call().get_themes().json()
            ]

            self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        expected_logging = [
            'INFO:root:[development] Available themes:',
            'INFO:root:[development] \t[1234] \tDefault Theme',
            'INFO:root:[development] \t[1235] \tTest Init Theme'
        ]
        self.assertEqual(cm.output, expected_logging)

        mock_write_config.assert_not_called()

    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_list_command_with_missing_theme_should_be_raise_message(
        self, mock_write_config, mock_gateway
    ):
        mock_gateway.return_value.get_themes.return_value.json.return_value = {
            "count": 0,
            "next": None,
            "previous": None,
            "results": []
        }
        with self.assertLogs(level='INFO') as cm:
            self.command.list(self.parser)
            expected_gateway_calls = [
                call(store='http://simple.com', apikey='2b78f637972b1c9d'),
                call().get_themes(),
                call().get_themes().json()
            ]

            self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        expected_logging = [
            'WARNING:root:[development] Missing Themes in http://simple.com'
        ]
        self.assertEqual(cm.output, expected_logging)

        mock_write_config.assert_not_called()

    #####
    # checkout
    #####
    def test_checkout_command_without_config_file_should_be_required_api_key_store_and_theme_id(self):
        with self.assertRaises(TypeError) as error:
            self.parser.apikey = None
            self.parser.store = None
            self.parser.theme_id = None
            self.command.checkout(self.parser)
        self.assertEqual(
            str(error.exception), '[development] argument -a/--apikey, -s/--store, -t/--theme_id are required.')

    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_checkout_command_with_theme_id_and_configs_should_be_download_file_correctly(
        self, mock_write_config, mock_gateway, mock_open_file
    ):
        mock_gateway.return_value.get_templates.return_value.json.return_value = [
            {
                "theme": 1,
                "name": "assets/image.png",
                "content": "",
                "file": "https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png"
            },
            {
                "theme": 1,
                "name": "layout/base.html",
                "content": "{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>",
                "file": None
            }
        ]
        mock_gateway.return_value._request.return_value.content = b'\xc2\x89'

        self.parser.filenames = None
        self.command.checkout(self.parser)

        expected_gateway_calls = [
            call(store='http://simple.com', apikey='2b78f637972b1c9d'),
            call().get_templates(1),
            call().get_templates().json(),
            # get image file
            call()._request('GET', 'https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png')
        ]

        self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        # create assets/image.png
        self.assertIn(call(os.path.join(os.getcwd(), 'assets/image.png'), 'wb'), mock_open_file.mock_calls)
        self.assertIn(call().__enter__().write(b'\xc2\x89'), mock_open_file.mock_calls)

        # create layout/base.html
        self.assertIn(
            call(os.path.join(os.getcwd(), 'layout/base.html'), 'w', encoding='utf-8'), mock_open_file.mock_calls)
        self.assertIn(call().__enter__().write(
            '{% load i18n %}\n\n<div class="mt-2">My home page</div>'), mock_open_file.mock_calls)

        mock_write_config.assert_called_once()

    #####
    # pull
    #####
    def test_pull_command_without_config_file_should_be_required_api_key_store_and_theme_id(self):
        with self.assertRaises(TypeError) as error:
            self.parser.apikey = None
            self.parser.store = None
            self.parser.theme_id = None
            self.command.pull(self.parser)
        self.assertEqual(
            str(error.exception), '[development] argument -a/--apikey, -s/--store, -t/--theme_id are required.')

    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_pull_command_with_configs_and_without_filename_should_be_download_all_files(
        self, mock_write_config, mock_gateway, mock_open_file
    ):
        mock_gateway.return_value.get_templates.return_value.json.return_value = [
            {
                "theme": 1,
                "name": "assets/image.png",
                "content": "",
                "file": "https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png"
            },
            {
                "theme": 1,
                "name": "layout/base.html",
                "content": "{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>",
                "file": None
            }
        ]
        mock_gateway.return_value._request.return_value.content = b'\xc2\x89'

        self.parser.filenames = None
        self.command.pull(self.parser)

        expected_gateway_calls = [
            call(store='http://simple.com', apikey='2b78f637972b1c9d'),
            call().get_templates(1),
            call().get_templates().json(),
            # get image file
            call()._request('GET', 'https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png')
        ]

        self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        # create assets/image.png
        self.assertIn(call(os.path.join(os.getcwd(), 'assets/image.png'), 'wb'), mock_open_file.mock_calls)
        self.assertIn(call().__enter__().write(b'\xc2\x89'), mock_open_file.mock_calls)

        # create layout/base.html
        self.assertIn(
            call(os.path.join(os.getcwd(), 'layout/base.html'), 'w', encoding='utf-8'), mock_open_file.mock_calls)
        self.assertIn(call().__enter__().write(
            '{% load i18n %}\n\n<div class="mt-2">My home page</div>'), mock_open_file.mock_calls)
        mock_write_config.assert_not_called()

    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    @patch("src.command.Config.write_config", autospec=True)
    def test_pull_command_with_configs_and_filenames_should_be_download_only_file_in_filenames(
        self, mock_write_config, mock_gateway, mock_open_file
    ):
        mock_gateway.return_value.get_template.return_value.json.return_value = {
            "theme": 1,
            "name": "assets/image.png",
            "content": "",
            "file": "https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png"
        }
        mock_gateway.return_value._request.return_value.content = b'\xc2\x89'

        self.parser.filenames = ["assets/image.png"]
        self.command.pull(self.parser)

        expected_gateway_calls = [
            call(store='http://simple.com', apikey='2b78f637972b1c9d'),
            call().get_template(1, 'assets/image.png'),
            call().get_template().json(),
            call()._request('GET', 'https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png')
        ]

        self.assertEqual(mock_gateway.mock_calls, expected_gateway_calls)

        # create assets/image.png
        self.assertIn(call(os.path.join(os.getcwd(), 'assets/image.png'), 'wb'), mock_open_file.mock_calls)
        self.assertIn(call().__enter__().write(b'\xc2\x89'), mock_open_file.mock_calls)

        mock_write_config.assert_not_called()

    #####
    # watch (_handle_files_change)
    #####
    @patch('src.command.Gateway', autospec=True)
    def test_watch_command_should_call_gateway_with_correct_arguments_belong_to_files_change(self, mock_gateway):
        mock_gateway.return_value.create_update_template.return_value.status_code = 200
        mock_gateway.return_value.delete_template.return_value.status_code = 200
        self.command.config.parser_config(self.parser)

        changes = {
            (Change.added, './assets/base.html'),
            (Change.modified, './layout/base.html'),
            (Change.deleted, './layout/base.html'),
        }

        with patch("builtins.open", self.mock_file):
            self.command._handle_files_change(changes)

            expected_call_init_gateway = call(store='http://simple.com', apikey='2b78f637972b1c9d')
            self.assertIn(expected_call_init_gateway, mock_gateway.mock_calls)

            # Change.added
            expected_call_added = call().create_update_template(1, payload={
                'name': 'assets/base.html',
                'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
            }, files={})
            self.assertIn(expected_call_added, mock_gateway.mock_calls)

            # Change.modified
            expected_call_modified = call().create_update_template(1, payload={
                'name': 'layout/base.html',
                'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
            }, files={})
            self.assertIn(expected_call_modified, mock_gateway.mock_calls)

            # Change.deleted
            expected_call_deleted = call().delete_template(1, 'layout/base.html')
            self.assertIn(expected_call_deleted, mock_gateway.mock_calls)

    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    def test_watch_command_with_create_image_file_should_call_gateway_with_correct_arguments(
        self, mock_gateway, mock_open_file
    ):
        mock_open_file.return_value = mock_img_file = MagicMock()
        self.command.config.parser_config(self.parser)

        mock_gateway.return_value.create_update_template.return_value.status_code = 200

        changes = [
            (Change.added, './assets/image.jpg'),
        ]

        self.command._handle_files_change(changes)

        # Change.added image
        expected_call_added = call().create_update_template(
            1,
            payload={'name': 'assets/image.jpg', 'content': ''},
            files={'file': ('assets/image.jpg', mock_img_file)}
        )
        self.assertIn(expected_call_added, mock_gateway.mock_calls)
