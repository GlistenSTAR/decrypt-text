# -*- coding: utf-8 -*-
import pytest
import io
from subbreaker.key import Key, AlphabetInvalid, KeyInvalid


def test_key_alphabet_lower():
    assert Key("abc", alphabet="ABc")._alphabet == "abc"


def test_key_double_char_in_alphabet():
    with pytest.raises(AlphabetInvalid, match=r"unique"):
        Key("abc", alphabet="aba")


def test_key_key_lower():
    assert Key("AbC", alphabet="abc")._key == "abc"


def test_key_double_char_in_key():
    with pytest.raises(KeyInvalid, match=r"unique"):
        Key("abca", alphabet="abcd")


def test_key_key_wrong_length():
    with pytest.raises(KeyInvalid, match=r"long"):
        Key("ab", alphabet="abc")
    with pytest.raises(KeyInvalid, match=r"long"):
        Key("abcd", alphabet="abc")


def test_key_key_incompatible_set():
    with pytest.raises(KeyInvalid, match=r"same set"):
        Key("abd", alphabet="abc")


def test_key_xcode():
    key = Key("abcdefghijklmnopqrstuvwxyz")
    assert key.decode("Hallo 23") == "Hallo 23"
    assert key.encode("Hallo 23") == "Hallo 23"


def test_key_xcode_file():
    key = Key("defghijklmnopqrstuvwxyzabc")
    output = io.StringIO()
    key.encode_file(plaintext_fh=io.StringIO("Hi there"), ciphertext_fh=output)
    assert output.getvalue() == "Kl wkhuh"
    output2 = io.StringIO()
    key.decode_file(ciphertext_fh=io.StringIO("Kl wkhuh"), plaintext_fh=output2)
    assert output2.getvalue() == "Hi there"
