import functools


def parser_config(*args, **kwargs):
    """Decorator for parser config values from command arguments."""

    def _wrapper(func):
        @functools.wraps(func)
        def _parser_config(self, parser, **func_kwargs):
            for name, value in kwargs.items():
                setattr(self.config, name, value)

            self.config.parser_config(parser, write_file=kwargs.get('write_file', False))
            self.gateway.store = self.config.store
            self.gateway.apikey = self.config.apikey

            func(self, parser, **func_kwargs)

        return _parser_config

    return _wrapper
