import asyncio
import logging
import os
import time

from watchgod import awatch
from watchgod.watcher import Change

from .gateway import Gateway
from .utils import create_and_get_config, progress_bar, get_config


logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

CONTENT_FILE_EXTENSIONS = ['.html', '.json', '.css', '.js']
MEDIA_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ico']


class Command:
    def _handle_files_change(self, changes, config):
        gateway = Gateway(store=config.store, apikey=config.apikey)
        for event_type, pathfile in changes:
            # change ./partials/alert_messages.html -> partials/alert_messages.html
            template_name = pathfile.replace('\\', '/').replace('./', '')
            current_pathfile = os.path.join(os.getcwd(), template_name)

            if current_pathfile.endswith(('.py', '.yml', '.conf')):
                return

            logging.info(f'[{config.env}] processing {template_name}')

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

                response = gateway.create_update_template(config.theme_id, payload=payload, files=files)
            elif event_type == Change.deleted:
                response = gateway.delete_template(config.theme_id, template_name)

            logging.info(f'[{config.env}] {str(event_type)} {template_name}')

            # api log error
            if not str(response.status_code).startswith('2'):
                result = response.json()
                error_msg = f'Can\'t update to theme id #{config.theme_id}.'
                if result.get('content'):
                    error_msg = ' '.join(result.get('content', []))
                if result.get('file'):
                    error_msg = ' '.join(result.get('file', []))
                logging.error(f'[{config.env}] {template_name} -> {error_msg}')

    def pull(self, parser):
        config = create_and_get_config(parser)

        gateway = Gateway(store=config.store, apikey=config.apikey)
        response = gateway.get_templates(config.theme_id)
        templates = response.json()

        if type(templates) != list:
            logging.info(f'Theme id #{config.theme_id} don\'t exist in the system.')
            return

        logging.info(f'[{config.env}] Connecting to {config.store}')
        logging.info(f'[{config.env}] Pulling files from theme id {config.theme_id} ')
        current_files = []
        for template in progress_bar(templates, prefix=f'[{config.env}] Progress:', suffix='Complete', length=50):
            template_name = str(template['name'])
            current_pathfile = os.path.join(os.getcwd(), template_name)
            current_files.append(current_pathfile.replace('\\', '/'))

            # create directories
            dirs = os.path.dirname(current_pathfile)
            if not os.path.exists(dirs):
                os.makedirs(dirs)

            # write file
            if template['file']:
                response = gateway._request("GET", template['file'])
                with open(current_pathfile, "wb") as media_file:
                    media_file.write(response.content)
                    media_file.close()
            else:
                with open(current_pathfile, "w", encoding="utf-8") as template_file:
                    template_file.write(template.get('content'))
                    template_file.close()

            time.sleep(0.01)

    def watch(self, parser):
        config = get_config(parser)
        logging.info(f'[{config.env}] Watching for file changes ')
        async def main():
            async for changes in awatch('.'):
                self._handle_files_change(changes, config)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
