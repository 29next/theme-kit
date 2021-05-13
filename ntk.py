#!/usr/bin/env python
import argparse
import asyncio
import collections
import logging
import os
import requests
import time

from watchgod import awatch
from watchgod.watcher import Change
import yaml

CONFIG_FILE_NAME = 'config.yml'
CONFIG_FILE = os.path.join(os.getcwd(), CONFIG_FILE_NAME)
CONTENT_FILE_EXTENSIONS = ['.html', '.json', '.css', '.js']
MEDIA_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ico']

Config = collections.namedtuple('Config', 'env apikey theme_id store')

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def _validate_config(apikey, theme_id, store):
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
        raise TypeError(f'argument {message} {pluralize} required')


def _get_config(parser, write_file=False):
    configs = {}
    env = parser.env
    if not os.path.exists(CONFIG_FILE):
        logging.warning(f'Could not find config file at {CONFIG_FILE}')
    else:
        with open(CONFIG_FILE, "r") as yamlfile:
            configs = yaml.load(yamlfile, Loader=yaml.FullLoader)
            yamlfile.close()

    if configs.get(env):
        if getattr(parser, 'apikey', None):
            configs[env]['apikey'] = parser.apikey

        if getattr(parser, 'theme_id', None):
            configs[env]['theme_id'] = parser.theme_id

        if getattr(parser, 'store', None):
            configs[env]['store'] = parser.store
    else:
        configs[getattr(parser, 'env')] = {
            "apikey": getattr(parser, 'apikey', None),
            "theme_id": getattr(parser, 'theme_id', None),
            "store": getattr(parser, 'store', None)
        }
    _validate_config(configs[env]['apikey'], configs[env]['theme_id'], configs[env]['store'])

    if write_file:
        with open(CONFIG_FILE, 'w') as yamlfile:
            yaml.dump(configs, yamlfile)
            yamlfile.close()

    return Config(
        env,
        configs[env]['apikey'],
        configs[env]['theme_id'],
        configs[env]['store']
    )


def _create_and_get_config(parser):
    config = {}
    env = parser.env
    if not os.path.exists(CONFIG_FILE):
        _validate_config(parser.apikey, parser.theme_id, parser.store)

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
        return _get_config(parser, write_file=True)


def _request(request_type, url, apikey=None, payload={}, files={}):
    headers = {}
    if apikey:
        headers = {'Authorization': f'Token {apikey}'}

    return requests.request(request_type, url, headers=headers, data=payload, files=files)


def _url(config_info):
    return f"{config_info.store}/api/admin/themes/{config_info.theme_id}/templates/"


def progressBar(iterable, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
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
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()


def _handle_files_change(changes, config_info):
    url = _url(config_info)
    for event_type, pathfile in changes:
        # change ./partials/alert_messages.html -> partials/alert_messages.html
        template_name = pathfile.replace('\\', '/').replace('./', '')
        current_pathfile = os.path.join(os.getcwd(), template_name)

        if current_pathfile.endswith(('.py', '.yml', '.conf')):
            return

        logging.info(f'[{config_info.env}] processing {template_name}')

        if event_type in [Change.added, Change.modified]:
            files = {}
            payload = {
                'name': template_name,
                'content': ''
            }

            if current_pathfile.endswith(tuple(MEDIA_FILE_EXTENSIONS)):
                files = {'file': (template_name, open(current_pathfile, 'rb'))}
            else:
                with open(current_pathfile, 'r') as f:
                    payload['content'] = f.read()
                    f.close()

            response = _request("POST", url, apikey=config_info.apikey, payload=payload, files=files)
        elif event_type == Change.deleted:
            response = _request("DELETE", f'{url}?name={template_name}', apikey=config_info.apikey)

        logging.info(f'[{config_info.env}] {str(event_type)} {template_name}')

        # api log error
        if not str(response.status_code).startswith('2'):
            result = response.json()
            error_msg = f'Can\'t update to theme id #{config_info.theme_id}.'
            if result.get('content'):
                error_msg = ' '.join(result.get('content', []))
            if result.get('file'):
                error_msg = ' '.join(result.get('file', []))
            logging.error(f'[{config_info.env}] {template_name} -> {error_msg}')


def pull(parser):
    config_info = _create_and_get_config(parser)

    response = _request("GET", _url(config_info), apikey=config_info.apikey)
    templates = response.json()

    if type(templates) != list:
        logging.info(f'Theme id #{config_info.theme_id} don\'t exist in the system.')
        return

    current_files = []
    for template in progressBar(templates, prefix=f'[{config_info.env}] Progress:', suffix='Complete', length=50):
        template_name = str(template['name'])
        current_pathfile = os.path.join(os.getcwd(), template_name)
        current_files.append(current_pathfile.replace('\\', '/'))

        # create directories
        dirs = os.path.dirname(current_pathfile)
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        # write file
        if template['file']:
            response = _request("GET", template['file'])
            with open(current_pathfile, "wb") as media_file:
                media_file.write(response.content)
                media_file.close()
        else:
            with open(current_pathfile, "w", encoding="utf-8") as template_file:
                template_file.write(template.get('content'))
                template_file.close()

        time.sleep(0.01)


def watch(parser):
    config_info = _get_config(parser)

    async def main():
        async for changes in awatch('.'):
            _handle_files_change(changes, config_info)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


def create_parser():
    def _add_config_arguments(parser):
        parser.add_argument('-a', '--apikey', action="store", dest="apikey", help='your API key')
        parser.add_argument('-s', '--store', action="store", dest="store", help='your store\'s URL')
        parser.add_argument(
            '-t', '--theme_id', action="store", dest="theme_id", help='your theme\'s ID is to download')
        parser.add_argument(
            '-e', '--env', action="store", dest="env", default='development',
            help='environment to run the command (default [development])')

    # create the top-level parser
    parser = argparse.ArgumentParser(
        epilog='Use "ntk [command] --help" for more information about a command.')
    _add_config_arguments(parser)
    subparsers = parser.add_subparsers(title='Available Commands')

    # create the parser for the "pull" command
    parser_pull = subparsers.add_parser('pull', help='Download a specific theme')
    parser_pull.set_defaults(func=pull)
    _add_config_arguments(parser_pull)

    # create the parser for the "watch" command
    parser_watch = subparsers.add_parser('watch', help='Push updates to your theme')
    parser_watch.set_defaults(func=watch)
    _add_config_arguments(parser_watch)

    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except TypeError as e:
        logging.error(e)
    except KeyboardInterrupt:
        pass
    except AttributeError:
        logging.error('unknown command for "ntk", please run "ntk -h"!')
