
import logging
import os
import yaml

CONFIG_FILE_NAME = 'config.yml'
CONFIG_FILE = os.path.join(os.getcwd(), CONFIG_FILE_NAME)

CONTENT_FILE_EXTENSIONS = ['.html', '.json', '.css', '.js']
MEDIA_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ico']


class Config(object):
    apikey = None
    store = None
    theme_id = None

    env = 'development'

    apikey_required = True
    store_required = True
    theme_id_required = True

    def __init__(self, **kwargs):
        self.read_config()
        for name, value in kwargs.items():
            setattr(self, name, value)

    def parser_config(self, parser, write_file=False):
        self.env = parser.env
        self.read_config()
        if getattr(parser, 'apikey', None):
            self.apikey = parser.apikey

        if getattr(parser, 'theme_id', None):
            self.theme_id = parser.theme_id

        if getattr(parser, 'store', None):
            self.store = parser.store

        self.save(write_file)

    def validate_config(self):
        error_msgs = []
        if self.apikey_required and not self.apikey:
            error_msgs.append('-a/--apikey')
        if self.store_required and not self.store:
            error_msgs.append('-s/--store')
        if self.theme_id_required and not self.theme_id:
            error_msgs.append('-t/--theme_id')
        if error_msgs:
            message = ', '.join(error_msgs)
            pluralize = 'is' if len(error_msgs) == 1 else 'are'
            raise TypeError(f'[{self.env}] argument {message} {pluralize} required.')

        return True

    def read_config(self, update=True):
        configs = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as yamlfile:
                configs = yaml.load(yamlfile, Loader=yaml.FullLoader)
                yamlfile.close()

            if configs and configs.get(self.env) and update:
                self.apikey = configs[self.env].get('apikey')
                self.store = configs[self.env].get('store')
                self.theme_id = configs[self.env].get('theme_id')
        return configs

    def write_config(self):
        configs = self.read_config(update=False)

        new_config = {
            'apikey': self.apikey,
            'store': self.store,
            'theme_id': self.theme_id
        }
        # If the config has been changed, then the config will be saved to config.yml.
        if configs.get(self.env) != new_config:
            configs[self.env] = new_config
            with open(CONFIG_FILE, 'w') as yamlfile:
                yaml.dump(configs, yamlfile)
                yamlfile.close()
            logging.info(f'[{self.env}] Configuration was updated.')

    def save(self, write_file=True):
        if self.validate_config() and write_file:
            self.write_config()
