import unittest


def test_suite():
    import logging

    logging.disable(logging.INFO)
    logging.disable(logging.WARNING)

    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    return suite
