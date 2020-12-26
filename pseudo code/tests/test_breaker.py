# -*- coding: utf-8 -*-
import pytest
from subbreaker.breaker import Breaker
from subbreaker.key import AlphabetInvalid


def test_generate_quadgrams_invalid_alphabet(fixturefiles_dir, tmp_path):
    input_file = str(fixturefiles_dir / "quadgram_corpus.txt")
    output_file = str(tmp_path / "XXX.json")
    with open(input_file) as in_fh, open(output_file, "w") as out_fh:
        with pytest.raises(AlphabetInvalid):
            Breaker.generate_quadgrams(in_fh, out_fh, alphabet="ABCDEa")


def test_generate_quadgrams(fixturefiles_dir, tmp_path):
    input_file = str(fixturefiles_dir / "quadgram_corpus.txt")
    output_file = str(tmp_path / "XXX.json")
    with open(input_file) as in_fh, open(output_file, "w") as out_fh:
        Breaker.generate_quadgrams(in_fh, out_fh)

    with open(output_file) as quadgram_fh, open(input_file) as text_fh:
        breaker = Breaker(quadgram_fh)
        assert round(breaker.calc_fitness_file(text_fh)) == 100


def test_quadgram_fitness(quadgram_fh):
    breaker = Breaker(quadgram_fh)
    text1 = (
        "The museum will be a lasting physical testament to his hard work and "
        "vision, and will house the prestigious collection he cared so deeply about, "
        "for many years to come."
    )
    text2 = (
        "Heute ist jeder Autohersteller in der Lage starke Motoren zu bauen, doch "
        "alles hat seine Grenzen, sonst waeren ja alle anderen die sich ans Gesetz "
        "halten die Dummen."
    )
    text3 = (
        "Agl qrxlrq okii bl t itxakhj ugexknti alxatqlha ad gkx gtsm odsy thm "
        "pkxkdh, thm okii gdrxl agl uslxakjkdrx ndiilnakdh gl ntslm xd mlluie tbdra, "
        "vds qthe eltsx ad ndql."
    )
    fitness1 = breaker.calc_fitness(text1)
    fitness2 = breaker.calc_fitness(text2)
    fitness3 = breaker.calc_fitness(text3)
    assert 95 < fitness1 < 105
    assert fitness3 < fitness2 < fitness1
    assert 130 < breaker.calc_fitness("tion")


def test_alphabet_too_long(fixturefiles_dir, tmp_path):
    input_file = str(fixturefiles_dir / "quadgram_corpus.txt")
    output_file = str(tmp_path / "XXX.json")
    with pytest.raises(AlphabetInvalid, match=r"characters"):
        with open(input_file) as in_fh, open(output_file, "w") as out_fh:
            Breaker.generate_quadgrams(
                in_fh, out_fh, alphabet="abcdefghijklmnopqrstuvwxyz0123456789",
            )


def test_text_too_short(quadgram_fh):
    breaker = Breaker(quadgram_fh)
    with pytest.raises(ValueError, match=r"three characters"):
        breaker.calc_fitness("346523230 a b 47146")
    with pytest.raises(ValueError, match=r"three characters"):
        breaker.calc_fitness("346523230 a b c 47146")


def test_break_text(quadgram_fh, fixed_ciphertext):
    breaker = Breaker(quadgram_fh)
    result = breaker.break_cipher(fixed_ciphertext)
    assert result.key.startswith("wisdom")
    assert 95 < result.fitness < 105
    assert str(result).startswith("key = wisdom")
    assert breaker.info.alphabet == "abcdefghijklmnopqrstuvwxyz"
    assert breaker.info.nbr_quadgrams > 90000000
    assert breaker.info.most_frequent_quadgram == "tion"
    assert 0 < breaker.info.average_fitness < 50
    assert 120 < breaker.info.max_fitness < 150
    assert breaker.key._alphabet == "abcdefghijklmnopqrstuvwxyz"
    assert breaker.key._key.startswith("wisdom")


def test_breaker_text_too_short(quadgram_fh):
    breaker = Breaker(quadgram_fh)
    with pytest.raises(ValueError, match=r"ciphertext is too short"):
        breaker.break_cipher("34623230 a b  c 47146")
    result = breaker.break_cipher("34623230 a b  c d47146", max_rounds=1)
    assert result.fitness > 0


def test_break_max_tries_invalid(quadgram_fh, fixed_ciphertext):
    breaker = Breaker(quadgram_fh)
    with pytest.raises(
        ValueError, match=r"maximum number of rounds not in the valid range"
    ):
        breaker.break_cipher(fixed_ciphertext, max_rounds=10001)


def test_break_consolidate_invalid(quadgram_fh, fixed_ciphertext):
    breaker = Breaker(quadgram_fh)
    with pytest.raises(ValueError, match=r"consolidate parameter out of valid range"):
        breaker.break_cipher(fixed_ciphertext, consolidate=31)
