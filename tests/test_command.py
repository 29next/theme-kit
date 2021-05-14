import os
import unittest
from unittest.mock import call, MagicMock, mock_open, patch

from watchgod.watcher import Change

from src.command import Command
from src.utils import Config


class TestCommand(unittest.TestCase):
    def setUp(self):
        config = {
            'env': 'development',
            'apikey': '2b78f637972b1c9d',
            'theme_id': '1',
            'store': 'http://simple.com'
        }
        self.parser = MagicMock(**config)
        self.config = Config(**config)
        self.command = Command()

        self.mock_file = mock_open(read_data='{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>')

    #####
    # pull
    #####
    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    @patch('src.command.create_and_get_config', autospec=True)
    def test_pull_command_should_create_files_belong_to_templates_response(
        self, mocker_config, mock_gateway, mock_open_file
    ):
        mocker_config.return_value = self.config
        mock_gateway.return_value.get_templates.return_value.json.return_value = [
            {
                "theme": '5',
                "name": "assets/image.png",
                "content": "",
                "file": "https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png"
            },
            {
                "theme": '5',
                "name": "layout/base.html",
                "content": "{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>",
                "file": None
            }
        ]
        mock_gateway.return_value._request.return_value.content = b'\xc2\x89'

        self.command.pull(self.parser)

        expected_gateway_calls = [
            call(store='http://simple.com', apikey='2b78f637972b1c9d'),
            call().get_templates('1'),
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

    #####
    # watch (_handle_files_change)
    #####
    @patch('src.command.Gateway', autospec=True)
    def test_watch_command_should_call_gateway_with_correct_arguments_belong_to_files_change(self, mock_gateway):
        mock_gateway.return_value.create_update_template.return_value.status_code = 200
        mock_gateway.return_value.delete_template.return_value.status_code = 200

        changes = {
            (Change.added, './assets/base.html'),
            (Change.modified, './layout/base.html'),
            (Change.deleted, './layout/base.html'),
        }

        with patch("builtins.open", self.mock_file):
            self.command._handle_files_change(changes, self.config)

            expected_call_init_gateway = call(store='http://simple.com', apikey='2b78f637972b1c9d')
            self.assertIn(expected_call_init_gateway, mock_gateway.mock_calls)

            # Change.added
            expected_call_added = call().create_update_template('1', payload={
                'name': 'assets/base.html',
                'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
            }, files={})
            self.assertIn(expected_call_added, mock_gateway.mock_calls)

            # Change.modified
            expected_call_modified = call().create_update_template('1', payload={
                'name': 'layout/base.html',
                'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
            }, files={})
            self.assertIn(expected_call_modified, mock_gateway.mock_calls)

            # Change.deleted
            expected_call_deleted = call().delete_template('1', 'layout/base.html')
            self.assertIn(expected_call_deleted, mock_gateway.mock_calls)

    @patch("builtins.open", autospec=True)
    @patch('src.command.Gateway', autospec=True)
    def test_watch_command_with_create_image_file_should_call_gateway_with_correct_arguments(
        self, mock_gateway, mock_open_file
    ):
        mock_open_file.return_value = mock_img_file = MagicMock()

        mock_gateway.return_value.create_update_template.return_value.status_code = 200

        changes = {
            (Change.added, './assets/image.jpg'),
        }

        self.command._handle_files_change(changes, self.config)

        # Change.added image
        expected_call_added = call().create_update_template('1', payload={
            'name': 'assets/image.jpg', 'content': ''},
            files={'file': ('assets/image.jpg', mock_img_file)})
        self.assertIn(expected_call_added, mock_gateway.mock_calls)
