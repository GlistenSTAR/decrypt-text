# -*- coding: utf-8 -*-
import pytest
import pathlib


@pytest.fixture
def fixturefiles_dir():
    return pathlib.Path(__file__).resolve().parent / "fixturefiles"


@pytest.fixture
def hello_txt(fixturefiles_dir):
    return str(fixturefiles_dir / "Hello.txt")


@pytest.fixture
def ciphertext_file_name(fixturefiles_dir):
    return str(fixturefiles_dir / "fixed_cipher.txt")


@pytest.fixture
def fixed_ciphertext(ciphertext_file_name):
    with open(ciphertext_file_name) as fh:
        ciphertext = fh.read()
    return ciphertext


@pytest.fixture
def quadgram_file():
    return (
        pathlib.Path(__file__).resolve().parents[1]
        / "subbreaker"
        / "quadgram"
        / "EN.json"
    )


@pytest.fixture
def quadgram_fh(quadgram_file):
    with open(str(quadgram_file)) as fh:
        yield fh
