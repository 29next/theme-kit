import collections
import logging
import os
import time
import yaml

from conf import CONFIG_FILE


Config = collections.namedtuple('Config', 'env apikey theme_id store')


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


def _validate_config(env, apikey, theme_id, store):
    error_msgs = []
    if not apikey:
        error_msgs.append('-a/--apikey')
    if not theme_id:
        error_msgs.append('-t/--theme_id')
    if not store:
        error_msgs.append('-s/--store')

    if error_msgs:
        message = ', '.join(error_msgs)
        pluralize = 'is' if len(error_msgs) == 1 else 'are'
        raise TypeError(f'[{env}] argument {message} {pluralize} required')


def get_config(parser, write_file=False):
    configs = {}
    env = parser.env
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f'Could not find config file at {CONFIG_FILE}')
    else:
        with open(CONFIG_FILE, "r") as yamlfile:
            configs = yaml.load(yamlfile, Loader=yaml.FullLoader)
            yamlfile.close()

    if configs and configs.get(env):
        if getattr(parser, 'apikey', None):
            configs[env]['apikey'] = parser.apikey

        if getattr(parser, 'theme_id', None):
            configs[env]['theme_id'] = parser.theme_id

        if getattr(parser, 'store', None):
            configs[env]['store'] = parser.store
    else:
        if configs is None:
            configs = {}

        configs[env] = {
            "apikey": getattr(parser, 'apikey', None),
            "theme_id": getattr(parser, 'theme_id', None),
            "store": getattr(parser, 'store', None)
        }

    _validate_config(env, configs[env]['apikey'], configs[env]['theme_id'], configs[env]['store'])

    is_config_update = False
    if getattr(parser, 'apikey', None) or getattr(parser, 'theme_id', None) or getattr(parser, 'store', None):
        is_config_update = True

    if write_file and is_config_update:
        with open(CONFIG_FILE, 'w') as yamlfile:
            yaml.dump(configs, yamlfile)
            yamlfile.close()

    return Config(
        env,
        configs[env]['apikey'],
        configs[env]['theme_id'],
        configs[env]['store']
    )


def create_and_get_config(parser):
    config = {}
    env = parser.env
    if not os.path.exists(CONFIG_FILE):
        _validate_config(env, parser.apikey, parser.theme_id, parser.store)

        config[env] = {
            "apikey": getattr(parser, 'apikey', None),
            "theme_id": getattr(parser, 'theme_id', None),
            "store": getattr(parser, 'store', None)
        }
        with open(CONFIG_FILE, 'w') as yamlfile:
            yaml.dump(config, yamlfile)
            yamlfile.close()

        return Config(env, config[env]['apikey'], config[env]['theme_id'], config[env]['store'])
    else:
        return get_config(parser, write_file=True)
