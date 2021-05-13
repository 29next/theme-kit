import unittest
from unittest.mock import call, MagicMock, patch

from src.gateway import Gateway


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.store = 'http://simple.com'
        self.apikey = 'apikey'

        self.gateway = Gateway(self.store, self.apikey)
        self.mock_img_file = MagicMock()

    #####
    # _request
    #####
    @patch('src.gateway.requests.request', autospec=True)
    def test_request(self, mock_request):
        request_type = 'POST'
        url = 'http://simple.com/api/admin/themes/5/templates/'
        payload = {
            'name': 'assets/base.html',
            'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
        }
        files = {'file': ('assets/image.jpg', self.mock_img_file)}

        self.gateway._request(request_type, url, apikey=self.apikey, payload=payload, files=files)

        expected_calls = [call(
            'POST', 'http://simple.com/api/admin/themes/5/templates/',
            headers={'Authorization': 'Token apikey'},
            data={'name': 'assets/base.html', 'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'},
            files=files)
        ]
        self.assertEqual(mock_request.mock_calls, expected_calls)

    #####
    # get_templates
    #####
    @patch('src.gateway.requests.request', autospec=True)
    def test_get_templates(self, mock_request):
        self.gateway.get_templates(6)

        expected_calls = [call(
            'GET', 'http://simple.com/api/admin/themes/6/templates/',
            headers={'Authorization': 'Token apikey'}, data={}, files={})]
        self.assertEqual(mock_request.mock_calls, expected_calls)

    #####
    # create_update_template
    #####
    @patch('src.gateway.requests.request', autospec=True)
    def test_create_update_template(self, mock_request):
        payload = {
            'name': 'assets/base.html',
            'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
        }
        files = {'file': ('assets/image.jpg', self.mock_img_file)}

        self.gateway.create_update_template(6, payload, files)

        expected_calls = [
            call(
                'POST', 'http://simple.com/api/admin/themes/6/templates/',
                headers={'Authorization': 'Token apikey'}, data=payload, files=files)
        ]
        self.assertEqual(mock_request.mock_calls, expected_calls)

    #####
    # delete_template
    #####
    @patch('src.gateway.requests.request', autospec=True)
    def test_delete_template(self, mock_request):
        self.gateway.delete_template(6, 'asset/custom.css')

        expected_calls = [
            call(
                'DELETE', 'http://simple.com/api/admin/themes/6/templates/?name=asset/custom.css',
                headers={'Authorization': 'Token apikey'}, data={}, files={})
        ]
        self.assertEqual(mock_request.mock_calls, expected_calls)
