import unittest
from unittest.mock import call, MagicMock, patch

from ntk.gateway import Gateway


class TestGateway(unittest.TestCase):
    def setUp(self):
        self.store = 'http://simple.com'
        self.apikey = 'apikey'

        self.gateway = Gateway(self.store, self.apikey)
        self.mock_img_file = MagicMock()

    #####
    # _request
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
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
    # get_themes
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_get_themes(self, mock_request):
        # check if call request failed
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'text/html'}

        with self.assertLogs(level='INFO') as log:
            self.gateway.get_themes()

        expected_logging = [
            'INFO:root:Missing Themes in http://simple.com'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.headers = {'content-type': 'application/json'}
        self.gateway.get_themes()

        expected_call = call('GET', 'http://simple.com/api/admin/themes/',
                             headers={'Authorization': 'Token apikey'}, data={}, files={})
        self.assertIn(expected_call, mock_request.mock_calls)

    ####
    # create_theme
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_create_theme(self, mock_request):
        # check if call request failed
        mock_request.return_value.headers = {'content-type': 'text/html'}

        with self.assertLogs(level='INFO') as log:
            self.gateway.create_theme(name="Test Init Theme")

        expected_logging = [
            'INFO:root:Theme "Test Init Theme" creation failed.'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'application/json'}
        payload = {
            "name": "Test Init Theme"
        }
        self.gateway.create_theme(name="Test Init Theme")

        expected_call = call('POST', 'http://simple.com/api/admin/themes/',
                             headers={'Authorization': 'Token apikey'}, data=payload, files={})
        self.assertIn(expected_call, mock_request.mock_calls)

    #####
    # get_templates
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_get_templates(self, mock_request):
        # check if call request failed
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'text/html'}

        with self.assertLogs(level='INFO') as log:
            self.gateway.get_templates(theme_id=6)

        expected_logging = [
            'INFO:root:Downloading templates files from theme id #6 failed.'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'application/json'}

        self.gateway.get_templates(theme_id=6)

        expected_call = call('GET', 'http://simple.com/api/admin/themes/6/templates/',
                             headers={'Authorization': 'Token apikey'}, data={}, files={})
        self.assertIn(expected_call, mock_request.mock_calls)

    #####
    # get_template
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_get_template(self, mock_request):
        template_name = 'assets/custom.css'
        # check if call request failed
        with self.assertLogs(level='INFO') as log:
            mock_request.return_value.ok = False
            self.gateway.get_template(theme_id=6, template_name=template_name)

        expected_logging = [
            'INFO:root:Downloading assets/custom.css file from theme id #6 failed.'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'application/json'}

        self.gateway.get_template(theme_id=6, template_name=template_name)

        expected_call = call('GET', f'http://simple.com/api/admin/themes/6/templates/?name={template_name}',
                             headers={'Authorization': 'Token apikey'}, data={}, files={})
        self.assertIn(expected_call, mock_request.mock_calls)

    #####
    # create_or_update_template
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_create_or_update_template(self, mock_request):
        # check if call request failed
        with self.assertLogs(level='INFO') as log:
            mock_request.return_value.ok = False
            self.gateway.create_or_update_template(theme_id=6, template_name='asset/custom.css')

        expected_logging = [
            'INFO:root:Uploading asset/custom.css file to theme id #6 failed.'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.ok = True
        mock_request.return_value.headers = {'content-type': 'application/json'}
        payload = {
            'name': 'assets/base.html',
            'content': '{% load i18n %}\n\n<div class="mt-2">My home page</div>'
        }
        files = {'file': ('assets/image.jpg', self.mock_img_file)}

        self.gateway.create_or_update_template(
            theme_id=6, template_name=payload['name'], content=payload['content'], files=files)

        expected_call = call('POST', 'http://simple.com/api/admin/themes/6/templates/',
                             headers={'Authorization': 'Token apikey'}, data=payload, files=files)
        self.assertIn(expected_call, mock_request.mock_calls)

    #####
    # delete_template
    #####
    @patch('ntk.gateway.requests.request', autospec=True)
    def test_delete_template(self, mock_request):
        mock_request.return_value.headers = {'content-type': 'application/json'}
        # check if call request failed
        with self.assertLogs(level='INFO') as log:
            mock_request.return_value.ok = False
            mock_request.return_value.json.return_value = {
                'name': ['This field is required.', 'Please enter filenames.']
            }
            self.gateway.delete_template(theme_id=6, template_name='asset/custom.css')

        expected_logging = [
            'INFO:root:Deleting asset/custom.css file from theme id #6 failed. -> "name" : '
            'This field is required. Please enter filenames.'
        ]
        self.assertEqual(log.output, expected_logging)

        # check if call request complated
        mock_request.return_value.ok = True
        self.gateway.delete_template(theme_id=6, template_name='asset/custom.css')

        expected_call = call('DELETE', 'http://simple.com/api/admin/themes/6/templates/?name=asset/custom.css',
                             headers={'Authorization': 'Token apikey'}, data={}, files={})
        self.assertIn(expected_call, mock_request.mock_calls)
