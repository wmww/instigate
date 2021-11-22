from core.text import *

from unittest import TestCase

class TestText(TestCase):
    def setUp(self) -> None:
        self.ctx = TextCtx(True)

    def test_from_str_to_str(self) -> None:
        raw = 'foo bar 123'
        self.assertEqual(from_str(raw).to_str(self.ctx), raw)

    def test_sequence_addition(self) -> None:
        text = from_str('foo') + from_str(' ') + from_str('bar')
        self.assertEqual(text.to_str(self.ctx), 'foo bar')
