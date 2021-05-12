#!/usr/bin/env python3
import argparse
import asyncio
import collections
import logging
import os
from watchgod import awatch
from watchgod.watcher import Change
import requests
import yaml

CONFIG_FILE = os.path.join(os.getcwd(), 'config.yml')

ConfigInfo = collections.namedtuple('ConfigInfo', 'apikey theme_id store')

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def _validate_config(apikey, theme_id, store):
    if not apikey:
        raise TypeError('argument -a/--apikey is required')
    if not theme_id:
        raise TypeError('argument -t/--theme_id is required')
    if not store:
        raise TypeError('argument -s/--store is required')


def _get_config(parser=None):
    # default config structure
    config = {
        "development": {
            "apikey": None,
            "theme_id": None,
            "store": None
        }
    }
    is_config_update = False

    if not os.path.exists(CONFIG_FILE):
        _validate_config(parser.apikey, parser.theme_id, parser.store)
    else:
        with open(CONFIG_FILE, "r") as yamlfile:
            config = yaml.load(yamlfile, Loader=yaml.FullLoader)
            yamlfile.close()

    if getattr(parser, 'apikey', None):
        is_config_update = True
        config['development']['apikey'] = parser.apikey

    if getattr(parser, 'theme_id', None):
        is_config_update = True
        config['development']['theme_id'] = parser.theme_id

    if getattr(parser, 'store', None):
        is_config_update = True
        config['development']['store'] = parser.store

    _validate_config(
        config.get('development', {}).get('apikey'),
        config.get('development', {}).get('theme_id'),
        config.get('development', {}).get('store'),
    )

    if is_config_update:
        with open(CONFIG_FILE, 'w') as yamlfile:
            yaml.dump(config, yamlfile)
            yamlfile.close()

    return ConfigInfo(
        config['development']['apikey'],
        config['development']['theme_id'],
        config['development']['store'],
    )


def _request(request_type, url, apikey=None, payload={}, files={}):
    headers = {}
    if apikey:
        headers = {'Authorization': 'Token {}'.format(apikey)}

    return requests.request(request_type, url, headers=headers, data=payload, files=files)


def _url(config_info):
    return "{}/api/admin/themes/{}/templates/".format(config_info.store, config_info.theme_id)


def _handle_templates_change(changes, config_info):
    url = _url(config_info)
    for event_type, pathfile in changes:
        # change ./partials/alert_messages.html -> partials/alert_messages.html
        template_name = pathfile.replace('./', '')
        current_pathfile = os.path.join(os.getcwd(), template_name)

        if current_pathfile.endswith(('.py', '.yml', '.conf')):
            return

        logging.info('{} {}'.format(str(event_type), template_name))

        if event_type in [Change.added, Change.modified]:
            files = {}
            payload = {
                'name': template_name,
                'content': ''
            }

            if current_pathfile.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                files = {'file': (template_name, open(current_pathfile, 'rb'))}
            else:
                with open(current_pathfile, 'r') as f:
                    payload['content'] = f.read()
                    f.close()

            response = _request("POST", url, apikey=config_info.apikey, payload=payload, files=files)
        elif event_type == Change.deleted:
            response = _request("DELETE", '{}?name={}'.format(url, template_name), apikey=config_info.apikey)

        # api log error
        if not str(response.status_code).startswith('2'):
            result = response.json()
            error_msg = 'Can\'t update to theme id #{}.'.format(config_info.theme_id)
            if result.get('content'):
                error_msg = ' '.join(result.get('content', []))
            logging.error('{} -> {}'.format(template_name, error_msg))


def pull(parser):
    config_info = _get_config(parser)

    response = _request("GET", _url(config_info), apikey=config_info.apikey)
    templates = response.json()

    if type(templates) != list:
        logging.info('Theme id #{} don\'t exist in the system.'.format(config_info.theme_id))
        return

    for template in templates:
        template_name = str(template['name'])
        current_pathfile = os.path.join(os.getcwd(), template_name)

        # create directories
        dirs = os.path.dirname(current_pathfile)
        if not os.path.exists(dirs):
            os.makedirs(dirs)

        # write html, css file
        if template['content']:
            with open(current_pathfile, "w", encoding="utf-8") as template_file:
                template_file.write(template['content'])
                template_file.close()

        # write media file
        if template['file']:
            response = _request("GET", template['file'])
            with open(current_pathfile, "wb") as media_file:
                media_file.write(response.content)
                media_file.close()

        logging.info('Downloading ' + template_name)


def watch(parser):
    config_info = _get_config()

    async def main():
        async for changes in awatch('.'):
            _handle_templates_change(changes, config_info)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


def create_parser():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='prime-theme-kit\'s commands', help='List command')

    # create the parser for the "pull" command
    parser_pull = subparsers.add_parser('pull', help='To download a specific theme')
    parser_pull.set_defaults(func=pull)
    parser_pull.add_argument(
        '-a', '--apikey', action="store", dest="apikey", help='your API key')
    parser_pull.add_argument('-s', '--store', action="store", dest="store", help='your store\'s URL')
    parser_pull.add_argument(
        '-t', '--theme_id', action="store", dest="theme_id", help='your theme\'s ID is to download')

    # create the parser for the "watch" command
    parser_watch = subparsers.add_parser('watch', help='Push updates to your theme')
    parser_watch.set_defaults(func=watch)

    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    args.func(args)
