import pytest

from msg_split import split_msg


def test_empty_msg():
    chunks = list(c for c in split_msg('', 1000))
    assert chunks == []


def test_zero_max_len():
    with pytest.raises(ValueError):
        for _ in split_msg('test', 0):
            pass


# def test_just_text():
#     text = 'a'*1024
#     chunks = list(c for c in split_msg(text, 128))
#     assert len(chunks) == 8


def test_splittable():
    text = ' <div><strong><i>' + 'a'*1024 + '</i></strong></div>'
    chunks = list(c for c in split_msg(text, 128))
    assert len(chunks) > 8

def test_unsplittable():
    text = '<a href=""><div><b>' + 'a'*1024 + '</b></div></a>'
    with pytest.raises(ValueError):
        list(c for c in split_msg(text, 128))
