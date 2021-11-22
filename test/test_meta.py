from unittest import TestCase
import logging

class TestMeta(TestCase):
    def test_can_log_info(self) -> None:
        logging.info('foo')

    def test_logging_warning_raises(self) -> None:
        with self.assertRaises(AssertionError):
            logging.warning('foo')

    def test_error_warning_raises(self) -> None:
        with self.assertRaises(AssertionError):
            logging.error('foo')
