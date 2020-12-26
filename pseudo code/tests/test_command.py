# -*- coding: utf-8 -*-
import sys
import re
import io
import json
import pytest

import subbreaker.command as command


def test_command_version(capsys):
    cmd = "subbreaker version"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert re.match(r"^\d+\.\d+\.\d+", captured.out)


def test_command_generate_quadgram(fixturefiles_dir, tmp_path):
    corpus = fixturefiles_dir / "quadgram_corpus.txt"
    quadgram_file = tmp_path / "YYY.json"
    cmd = "subbreaker quadgrams --corpus {} --quadgrams {}".format(
        str(corpus), str(quadgram_file)
    )
    sys.argv = cmd.split()
    command.main()
    with open(str(quadgram_file)) as fh:
        obj = json.load(fh)
    assert obj["alphabet"] == "abcdefghijklmnopqrstuvwxyz"
    assert type(obj["nbr_quadgrams"]) == int
    assert type(obj["most_frequent_quadgram"]) == str
    assert type(obj["max_fitness"]) == int
    assert type(obj["average_fitness"]) == float
    assert type(obj["quadgrams"]) == list
    assert type(obj["quadgrams"][0]) == int
    assert len(obj["quadgrams"]) == 32 * 32 * 32 * 32


def test_command_fitness_text(capsys):
    cmd = "subbreaker fitness --text Hello --lang EN"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert 20 < float(captured.out) < 120


def test_command_fitness_file(capsys, fixturefiles_dir):
    text_file = fixturefiles_dir / "quadgram_corpus.txt"
    cmd = "subbreaker fitness --plaintext {} --lang EN".format(str(text_file))
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert 95 < float(captured.out) < 105


def test_command_decode_text(capsys):
    cmd = "subbreaker decode --text Khoor --key defghijklmnopqrstuvwxyzabc"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello"


def test_command_decode_double_char_in_alphabet(capsys):
    cmd = "subbreaker decode --text Khoor --key abcde --alphabet abcdc"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker decode")
    assert "subbreaker decode: error:" in captured.err
    assert "unique" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_decode_double_char_in_key(capsys):
    cmd = "subbreaker decode --text Khoor --key abcdc --alphabet abcde"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker decode")
    assert "subbreaker decode: error:" in captured.err
    assert "unique" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_decode_alphabet_key_unequal_length(capsys):
    cmd = "subbreaker decode --text Khoor --key abcd --alphabet abcde"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker decode")
    assert "subbreaker decode: error:" in captured.err
    assert "long" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_decode_alphabet_key_incompatible_set(capsys):
    cmd = "subbreaker decode --text Khoor --key abcd --alphabet abce"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker decode")
    assert "subbreaker decode: error:" in captured.err
    assert "same set" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_decode_keyword(capsys):
    cmd = "subbreaker decode --text zebrascdfghijklmnopqtuvwxy --keyword Zebrasber"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "abcdefghijklmnopqrstuvwxyz"


def test_command_decode_file(capsys, hello_txt):
    cmd = "subbreaker decode --ciphertext {} --key defghijklmnopqrstuvwxyzabc".format(
        hello_txt
    )
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Ebiil"


def test_command_decode_no_args(capsys):
    sys.argv = "subbreaker decode".split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker decode")
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_text(capsys):
    cmd = "subbreaker encode --text Hello --key defghijklmnopqrstuvwxyzabc"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Khoor"


def test_command_encode_file(capsys, hello_txt):
    cmd = "subbreaker encode --plaintext {} --key defghijklmnopqrstuvwxyzabc".format(
        hello_txt
    )
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Khoor"


def test_command_encode_no_args(capsys):
    sys.argv = "subbreaker encode".split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert "--key" in captured.err
    assert "--random" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_double_char_in_alphabet(capsys):
    cmd = "subbreaker encode --text Khoor --key abcde --alphabet abcdc"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker encode")
    assert "subbreaker encode: error:" in captured.err
    assert "unique" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_double_char_in_key(capsys):
    cmd = "subbreaker encode --text Khoor --key abcdc --alphabet abcde"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker encode")
    assert "subbreaker encode: error:" in captured.err
    assert "unique" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_alphabet_key_unequal_length(capsys):
    cmd = "subbreaker encode --text Khoor --key abcd --alphabet abcde"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker encode")
    assert "subbreaker encode: error:" in captured.err
    assert "long" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_alphabet_key_incompatible_set(capsys):
    cmd = "subbreaker encode --text Khoor --key abcd --alphabet abce"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker encode")
    assert "subbreaker encode: error:" in captured.err
    assert "same set" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_encode_random(capsys):
    cmd = "subbreaker encode --text Hello --random"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    key = captured.err.strip()
    ciphertext = captured.out.strip()
    cmd = "subbreaker decode --text {} --key {}".format(ciphertext, key)
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello"


def test_command_encode_keyword(capsys):
    cmd = "subbreaker encode --text abcdefghijklmnopqrstuvwxyz --keyword Zebrasber"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "zebrascdfghijklmnopqtuvwxy"


def test_command_break_text(capsys, fixed_ciphertext):
    cmd = "subbreaker break --text"
    sys.argv = cmd.split() + [fixed_ciphertext]
    command.main()
    captured = capsys.readouterr()
    assert "Alphabet: abcdefghijklmnopqrstuvwxyz" in captured.out
    assert "Key:      wisdom" in captured.out
    assert "Fitness: 10" in captured.out
    assert "The trouble with having an open mind," in captured.out


def test_command_break_file(capsys, ciphertext_file_name):
    cmd = "subbreaker break --ciphertext {}".format(ciphertext_file_name)
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert "Alphabet: abcdefghijklmnopqrstuvwxyz" in captured.out
    assert "Key:      wisdom" in captured.out
    assert "Fitness: 10" in captured.out
    assert "The trouble with having an open mind," in captured.out


def test_command_break_invalid_max_tries(capsys):
    cmd = "subbreaker break --max-tries 10001"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker break")
    assert "subbreaker break: error:" in captured.err
    assert "must be in the range" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_break_invalid_consolidate(capsys):
    cmd = "subbreaker break --consolidate 31"
    sys.argv = cmd.split()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        command.main()
    captured = capsys.readouterr()
    assert captured.err.startswith("usage: subbreaker break")
    assert "subbreaker break: error:" in captured.err
    assert "must be in the range" in captured.err
    assert pytest_wrapped_e.value.code == 2


def test_command_break_no_args(monkeypatch, fixed_ciphertext, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(fixed_ciphertext))
    sys.argv = "subbreaker break".split()
    command.main()
    captured = capsys.readouterr()
    assert "Alphabet: abcdefghijklmnopqrstuvwxyz" in captured.out
    assert "Key:      wisdom" in captured.out
    assert "Fitness: 10" in captured.out
    assert "The trouble with having an open mind," in captured.out


def test_command_info(capsys):
    cmd = "subbreaker info"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert "Quadgram file:" in captured.out
    assert "subbreaker/quadgram/EN.json" in captured.out
    assert "Alphabet: abcdefghijklmnopqrstuvwxyz" in captured.out
    assert "Length of alphabet: 26" in captured.out
    assert "Number of quagrams:" in captured.out
    assert "Most frequent quadgram: tion" in captured.out
    assert "Fitness for most frequent quadgram: 13" in captured.out
    assert "Fitness for random text: 2" in captured.out


def test_no_command(capsys):
    cmd = "subbreaker"
    sys.argv = cmd.split()
    command.main()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage: subbreaker [-h]")
    assert "A collection of tools" in captured.out
