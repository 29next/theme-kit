import os
import pytest
from watchgod.watcher import Change
from unittest.mock import call, MagicMock, mock_open

import ntk


class TestNtk:
    #####
    # _validate_config
    #####
    def test_validate_config_should_raise_expected_error(self):
        with pytest.raises(TypeError):
            ntk._validate_config(None, '1', 'http://simple.com')

        with pytest.raises(TypeError):
            ntk._validate_config('apikey', None, 'http://simple.com')

        with pytest.raises(TypeError):
            ntk._validate_config('apikey', '1', None)

    #####
    # _get_config
    #####
    def test_get_config_with_file_not_exist_should_write_file_and_retrun_expected_config_info(self, mocker):
        mocker.patch("ntk.os.path.exists").return_value = False
        mock_open_file = mocker.patch("builtins.open")
        parser = MagicMock(apikey='apikey', theme_id='1', store='http://simple.com')

        config_info = ntk._get_config(parser)

        mock_open_file.assert_called_once_with(os.path.join(os.getcwd(), 'config.yml'), 'w')

        assert config_info.apikey == 'apikey'
        assert config_info.theme_id == '1'
        assert config_info.store == 'http://simple.com'

    def test_get_config_with_file_exists_should_get_config_info_from_file(self, mocker):
        mocker.patch("builtins.open", mock_open(
            read_data='development:\n  apikey: 2b78f637972b1c9d\n  store: http://simple.com\n  theme_id: "1"\n'))
        mocker.patch("ntk.os.path.exists").return_value = True

        config_info = ntk._get_config()

        assert config_info.apikey == '2b78f637972b1c9d'
        assert config_info.theme_id == '1'
        assert config_info.store == 'http://simple.com'

    def test_get_config_with_file_exists_and_parser_should_update_config_belong_to_parser_and_retrun_expected_config(
        self, mocker
    ):
        mocker.patch("ntk.os.path.exists").return_value = True
        parser = MagicMock(apikey=None, theme_id='2', store='http://sandbox.29next.com')
        mock_open_file = mocker.patch("builtins.open", mock_open(
            read_data='development:\n  apikey: 2b78f637972b1c9d\n  store: http://simple.com\n  theme_id: "1"\n'))

        config_info = ntk._get_config(parser)

        assert call(os.path.join(os.getcwd(), 'config.yml'), 'r') in mock_open_file.mock_calls
        assert call(os.path.join(os.getcwd(), 'config.yml'), 'w') in mock_open_file.mock_calls

        # update store and theme_id in config file
        assert call().write('store') in mock_open_file.mock_calls
        assert call().write('http://sandbox.29next.com') in mock_open_file.mock_calls
        assert call().write('theme_id') in mock_open_file.mock_calls
        assert call().write('2') in mock_open_file.mock_calls

        assert config_info.apikey == '2b78f637972b1c9d'
        assert config_info.theme_id == '2'
        assert config_info.store == 'http://sandbox.29next.com'

    #####
    # _request
    #####
    def test_request_should_call_with_expected_argument(self, mocker):
        mock_request = mocker.patch("ntk.requests.request")
        # mock_request.return_value = None

        payload = {
            'name': 'xxx.html'
        }
        ntk._request('GET', 'http://simple.com/themes/templates', apikey='2b78f637972b1c9d', payload=payload)

        expected_calls = [
            call(
                'GET', 'http://simple.com/themes/templates',
                headers={'Authorization': 'Token 2b78f637972b1c9d'}, data=payload, files={})
        ]
        assert mock_request.mock_calls == expected_calls

    #####
    # _url
    #####
    def test_url_should_return_store_url_join_with_api_themes_templates(self):
        config_info = MagicMock(store='http://simple.com', theme_id='5')
        url = ntk._url(config_info)

        assert url == 'http://simple.com/api/admin/themes/5/templates/'

    #####
    # pull
    #####
    def test_pull_template_should_create_template_belong_to_api_templates_response(self, mocker):
        mock_request = mocker.patch('ntk._request')
        mock_path_exists = mocker.patch('ntk.os.path.exists')
        mock_path_exists.return_value = True

        templates_response = [
            {
                "theme": '5',
                "name": "assets/image.png",
                "content": "",
                "file": "https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png"
            },
            {
                "theme": 5,
                "name": "layout/base.html",
                "content": "{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>",
                "file": None
            }
        ]
        mock_request.return_value.json.return_value = templates_response
        mock_request.return_value.content = b'\xc2\x89'

        mock_config = mocker.patch("ntk._get_config")
        mock_config.return_value = parser = MagicMock(apikey='apikey', theme_id='1', store='http://simple.com')

        mock_open_file = mocker.patch("builtins.open")

        ntk.pull(parser)

        expected_call_requests = [
            call('GET', 'http://simple.com/api/admin/themes/1/templates/', apikey='apikey'),
            call().json(),
            # get image file from S3
            call('GET', 'https://d36qje162qkq4w.cloudfront.net/media/sandbox/themes/5/assets/image.png')
        ]
        assert mock_request.mock_calls == expected_call_requests

        # create assets/image.png
        assert call(os.path.join(os.getcwd(), 'assets/image.png'), 'wb') in mock_open_file.mock_calls
        assert call().__enter__().write(b'\xc2\x89') in mock_open_file.mock_calls

        # create layout/base.html
        assert call(os.path.join(os.getcwd(), 'layout/base.html'), 'w', encoding='utf-8') in mock_open_file.mock_calls
        assert call().__enter__().write(
            '{% load i18n %}\n\n<div class="mt-2">My home page</div>') in mock_open_file.mock_calls

    #####
    # _handle_templates_change
    #####
    def test_handle_templates_change_should_call_request_with_correct_arguments(self, mocker):
        mocker.patch("builtins.open", mock_open(
            read_data='{% load i18n %}\n\n<div class=\"mt-2\">My home page</div>'))

        mock_request = mocker.patch('ntk.requests.request')
        mock_request.return_value.status_code = 200

        config_info = MagicMock(apikey='apikey', theme_id='1', store='http://simple.com')

        changes = {
            (Change.added, './assets/base.html'),
            (Change.modified, './layout/base.html'),
            (Change.deleted, './layout/base.html'),
        }

        ntk._handle_templates_change(changes, config_info)

        assert mock_request.call_count == 3

        # Change.modified
        expected_call_modified = call(
            'POST', 'http://simple.com/api/admin/themes/1/templates/',
            headers={'Authorization': 'Token apikey'},
            data={'name': 'layout/base.html', 'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'},
            files={})
        assert expected_call_modified in mock_request.mock_calls

        # Change.deleted
        expected_call_deleted = call(
            'DELETE', 'http://simple.com/api/admin/themes/1/templates/?name=layout/base.html',
            headers={'Authorization': 'Token apikey'}, data={}, files={})
        assert expected_call_deleted in mock_request.mock_calls

        # Change.added
        expected_call_added = call(
            'POST', 'http://simple.com/api/admin/themes/1/templates/',
            headers={'Authorization': 'Token apikey'},
            data={'name': 'layout/base.html', 'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'},
            files={})
        assert expected_call_added in mock_request.mock_calls

    def test_handle_templates_change_with_image_file_should_call_request_with_correct_arguments(self, mocker):
        mock_open_file = mocker.patch("builtins.open")
        mock_open_file.return_value = mock_img_file = MagicMock()

        mock_request = mocker.patch('ntk.requests.request')
        mock_request.return_value.status_code = 200

        config_info = MagicMock(apikey='apikey', theme_id='1', store='http://simple.com')

        changes = {
            (Change.added, './assets/image.jpg'),
        }

        ntk._handle_templates_change(changes, config_info)

        assert mock_request.call_count == 1

        # Change.added image
        expected_call_added = call(
            'POST', 'http://simple.com/api/admin/themes/1/templates/',
            headers={'Authorization': 'Token apikey'}, data={'name': 'assets/image.jpg', 'content': ''},
            files={'file': ('assets/image.jpg', mock_img_file)})
        assert expected_call_added in mock_request.mock_calls
