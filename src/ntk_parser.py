import argparse

from command import Command


class Parser:
    def __init__(self):
        self.command = Command()

    def _add_config_arguments(self, parser):
        parser.add_argument('-a', '--apikey', action="store", dest="apikey", help=argparse.SUPPRESS)
        parser.add_argument('-s', '--store', action="store", dest="store", help=argparse.SUPPRESS)
        parser.add_argument(
            '-t', '--theme_id', action="store", dest="theme_id", help=argparse.SUPPRESS)
        parser.add_argument(
            '-e', '--env', action="store", dest="env", default='development', help=argparse.SUPPRESS)

    def create_parser(self):
        option_commands = '''
options:
    -a, --apikey        API key
    -s, --store         Store URL
    -t, --theme_id      Theme ID
    -e, --env           Environment to run the command(default [development])'''

        # create the top-level parser
        parser = argparse.ArgumentParser(
            description='''
Usage:
    ntk [command] [options]

available commands:
    pull        Download all files from a theme
    watch       Push updates to your theme
''' + option_commands,
            usage=argparse.SUPPRESS,
            epilog='Use "ntk [command] --help" for more information about a command.',
            formatter_class=argparse.RawTextHelpFormatter,
            add_help=argparse.SUPPRESS
        )
        subparsers = parser.add_subparsers(title='Available Commands', help=argparse.SUPPRESS)

        # create the parser for the "pull" command
        parser_pull = subparsers.add_parser(
            'pull',
            help='Download a specific theme',
            usage=argparse.SUPPRESS,
            description='''
Usage:
    ntk pull [options]
''' + option_commands,
            formatter_class=argparse.RawTextHelpFormatter)
        parser_pull.set_defaults(func=self.command.pull)
        self._add_config_arguments(parser_pull)

        # create the parser for the "watch" command
        parser_watch = subparsers.add_parser(
            'watch',
            help='Push updates to your theme',
            usage=argparse.SUPPRESS,
            description='''
Usage:
    ntk watch [options]
''' + option_commands,
            formatter_class=argparse.RawTextHelpFormatter)
        parser_watch.set_defaults(func=self.command.watch)
        self._add_config_arguments(parser_watch)

        return parser
