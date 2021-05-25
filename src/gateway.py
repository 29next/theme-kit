import requests


class Gateway:
    def __init__(self, store, apikey):
        self.store = store
        self.apikey = apikey

    def _request(self, request_type, url, apikey=None, payload={}, files={}):
        headers = {}
        if apikey:
            headers = {'Authorization': f'Token {apikey}'}

        return requests.request(request_type, url, headers=headers, data=payload, files=files)

    def get_themes(self):
        url = f"{self.store}/api/admin/themes/"

        return self._request("GET", url, apikey=self.apikey)

    def create_theme(self, payload):
        url = f"{self.store}/api/admin/themes/"

        return self._request("POST", url, apikey=self.apikey, payload=payload)

    def get_template(self, theme_id, filename):
        url = f"{self.store}/api/admin/themes/{theme_id}/templates/?name={filename}"

        return self._request("GET", url, apikey=self.apikey)

    def get_templates(self, theme_id):
        url = f"{self.store}/api/admin/themes/{theme_id}/templates/"

        return self._request("GET", url, apikey=self.apikey)

    def create_update_template(self, theme_id, payload, files):
        url = f"{self.store}/api/admin/themes/{theme_id}/templates/"

        return self._request("POST", url, apikey=self.apikey, payload=payload, files=files)

    def delete_template(self, theme_id, template_name):
        url = f"{self.store}/api/admin/themes/{theme_id}/templates/?name={template_name}"

        return self._request("DELETE", url, apikey=self.apikey)
