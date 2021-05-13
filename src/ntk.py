#!/usr/bin/env python
import logging

from src.parser import Parser

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)


def main():
    parser = Parser().create_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except TypeError as e:
        logging.error(e)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
