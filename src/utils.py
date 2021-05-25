import logging
import os
import time
import yaml

from conf import CONFIG_FILE


def progress_bar(iterable, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    if total == 0:
        return

    # Progress Bar Printing Function
    def print_progress_bar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f'\r{current_time} INFO {prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    # Initial Call
    print_progress_bar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        print_progress_bar(i + 1)
    # Print New Line on Complete
    print()


class Config(object):
    apikey = None
    store = None
    theme_id = None

    env = 'development'

    apikey_required = True
    store_required = True
    theme_id_required = True

    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)

    def parser_config(self, parser, write_file=False):
        self.read_config()
        self.env = parser.env
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

    def read_config(self):
        if not os.path.exists(CONFIG_FILE):
            logging.warning(f'Could not find config file at {CONFIG_FILE}')
        else:
            with open(CONFIG_FILE, "r") as yamlfile:
                configs = yaml.load(yamlfile, Loader=yaml.FullLoader)
                yamlfile.close()

            if configs and configs.get(self.env):
                self.apikey = configs[self.env].get('apikey')
                self.store = configs[self.env].get('store')
                self.theme_id = configs[self.env].get('theme_id')

    def write_config(self):
        configs = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as yamlfile:
                configs = yaml.load(yamlfile, Loader=yaml.FullLoader)
                yamlfile.close()

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
