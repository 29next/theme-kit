#!/usr/bin/env python
import logging

from ntk_parser import Parser

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    parser = Parser().create_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print('Use ntk -h to see available commands')
    except TypeError as e:
        logging.error(e)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
