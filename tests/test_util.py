from util import *


def test_fmt_float():
    assert '1,234,567.56' == fmt_float(1234567.56)
    assert '123,456.56' == fmt_float(123456.56)
    assert '1,234.56' == fmt_float(1234.56)
    assert '-1,234.56' == fmt_float(-1234.56)
    assert '234.56' == fmt_float(234.56)
    assert '-234.56' == fmt_float(-234.56)
    assert '234' == fmt_float(234)
    assert '234.1' == fmt_float(234.1)
    assert '-234' == fmt_float(-234)
    assert '0' == fmt_float(0)
