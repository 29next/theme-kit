
import logging
import os
import yaml

CONFIG_FILE_NAME = './config.yml'
CONFIG_FILE = os.path.abspath(CONFIG_FILE_NAME)

CONTENT_FILE_EXTENSIONS = ['.html', '.json', '.css', '.js']
MEDIA_FILE_EXTENSIONS = [
    '.woff2', '.gif', '.ico', '.png', '.jpg', '.jpeg', '.svg', '.eot', '.tff', '.ttf', '.woff',
    '.webp', '.mp4', '.webm', '.mp3', '.pdf',
]

SASS_EXTENSIONS = ['.scss']

SASS_SOURCE = 'sass'
SASS_DESTINATION = 'assets'
SASS_OUTPUT_STYLES = ['nested', 'expanded', 'compact', 'compressed']

# Tailwind CSS defaults
TAILWIND_INPUT = 'css/input.css'
TAILWIND_OUTPUT = 'assets/main.css'
TAILWIND_BINARY_NAMES = ['./tailwindcss', 'tailwindcss', 'npx tailwindcss']
TAILWIND_V4_MARKER = '@import "tailwindcss"'
TAILWIND_V3_CONFIG = 'tailwind.config.js'
TAILWIND_SASS_COMPAT = 'scripts/sass-compat.py'

GLOB_PATTERN = [
    "assets/**/*.html",
    "assets/**/*.json",
    "assets/**/*.css",
    "assets/**/*.scss",
    "assets/**/*.js",

    "assets/**/*.woff2",
    "assets/**/*.gif",
    "assets/**/*.ico",
    "assets/**/*.png",
    "assets/**/*.jpg",
    "assets/**/*.jpeg",
    "assets/**/*.svg",
    "assets/**/*.eot",
    "assets/**/*.tff",
    "assets/**/*.ttf",
    "assets/**/*.woff",
    "assets/**/*.webp",
    "assets/**/*.mp4",
    "assets/**/*.webm",
    "assets/**/*.mp3",
    "assets/**/*.pdf",
    "checkout/**/*.html",
    "configs/**/*.json",
    "layouts/**/*.html",
    "partials/**/*.html",
    "templates/**/*.html",
    "locales/**/*.json",

    f"{SASS_SOURCE}/**/*.scss",
]


class Config(object):
    apikey = None
    store = None
    theme_id = None
    sass_output_style = None

    # Tailwind config
    tailwind_input = None
    tailwind_output = None
    tailwind_binary = None
    tailwind_sass_compat = None

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

        if getattr(parser, 'sass_output_style', None):
            self.sass_output_style = parser.sass_output_style

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

        if self.sass_output_style and self.sass_output_style not in SASS_OUTPUT_STYLES:
            raise TypeError(
                f'[{self.env}] argument -sos/--sass_output_style is unsupported '
                'output_style; choose one of nested, expanded, compact, and compressed')

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
                if configs[self.env].get('sass'):
                    self.sass_output_style = configs[self.env]['sass'].get('output_style')
                if configs[self.env].get('tailwind') is not None:
                    tw = configs[self.env]['tailwind']
                    self.tailwind_input = tw.get('input', TAILWIND_INPUT)
                    self.tailwind_output = tw.get('output', TAILWIND_OUTPUT)
                    self.tailwind_binary = tw.get('binary')
                    self.tailwind_sass_compat = tw.get('sass_compat')

        return configs

    def detect_tailwind(self):
        """Auto-detect Tailwind CSS setup if not explicitly configured."""
        if self.tailwind_input and self.tailwind_binary:
            return True  # Already configured

        # Check for Tailwind v4 (CSS-based config with @import "tailwindcss")
        input_file = self.tailwind_input or TAILWIND_INPUT
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    content = f.read(1024)  # Only need the first kilobyte
                if TAILWIND_V4_MARKER in content:
                    self.tailwind_input = input_file
                    self.tailwind_output = self.tailwind_output or TAILWIND_OUTPUT
            except (OSError, UnicodeDecodeError):
                pass

        # Check for Tailwind v3 (JS config file)
        if not self.tailwind_input and os.path.exists(TAILWIND_V3_CONFIG):
            self.tailwind_input = TAILWIND_INPUT if os.path.exists(TAILWIND_INPUT) else None
            self.tailwind_output = self.tailwind_output or TAILWIND_OUTPUT

        if not self.tailwind_input:
            return False

        # Find binary if not configured
        if not self.tailwind_binary:
            import shutil
            for binary in TAILWIND_BINARY_NAMES:
                if binary.startswith('./'):
                    if os.path.isfile(binary) and os.access(binary, os.X_OK):
                        self.tailwind_binary = binary
                        break
                elif shutil.which(binary):
                    self.tailwind_binary = binary
                    break

        # Detect sass-compat.py if not configured
        if not self.tailwind_sass_compat and os.path.exists(TAILWIND_SASS_COMPAT):
            self.tailwind_sass_compat = TAILWIND_SASS_COMPAT

        return self.tailwind_binary is not None

    def write_config(self):
        configs = self.read_config(update=False)

        new_config = {
            'apikey': self.apikey,
            'store': self.store,
            'theme_id': self.theme_id,
            'sass': {
                'output_style': self.sass_output_style or 'nested'  # default sass output style is nested
            }
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
