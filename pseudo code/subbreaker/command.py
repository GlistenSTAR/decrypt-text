# -*- coding: utf-8 -*-
"""Module containing the CLI implementation
"""
import argparse
import sys
import random
import pathlib
from contextlib import contextmanager

from subbreaker.key import Key, AlphabetInvalid, KeyInvalid
from subbreaker.version import __version__
from subbreaker.breaker import Breaker

quadgram_dir = pathlib.Path(__file__).resolve().parent / "quadgram"


@contextmanager
def open_file(file_name, mode="r"):
    """Unify handling of stdin/stdout and files to read from resp. write to

    This is a helper function which can be used with context managers.

    :param file_name: The name of the file (full path) to read from. If None is given,
        stdin will be used
    :type file_name: str or None
    :param str mode: The mode used to open the file, defaults to "r"
    """
    default = sys.stdin if "r" in mode else sys.stdout
    fh = default if file_name is None else open(file_name, mode)
    try:
        yield fh
    finally:
        if file_name is not None:
            fh.close()


def consistency_check(args, alphabet, key):
    """Checks the alphabet and the key for consistency and normalizes both to lower case

    :param object args: object containing the converted arguments
    :param str alphabet: the untrusted alphabet to check
    :param str key: the untrusted key to check
    :return: a tuple of the validated alphabet and key. Both are returned in lower case.
    :rtype: tuple(str, str)
    """
    try:
        alphabet = Key.check_alphabet(alphabet)
        key = Key.check_key(key, alphabet)
    except (AlphabetInvalid, KeyInvalid) as exc:
        args.subparser.error(str(exc))
    return alphabet, key


def build_key_from_keyword(args):
    """In case a keyword was given, determine the corresponding key

    :param object args: object containing the converted arguments
    """
    alpha_list = list(args.alphabet.lower())
    kw_list = []
    for char in args.keyword.lower():
        if char not in kw_list:
            kw_list.append(char)
            alpha_list.remove(char)
    return "".join(kw_list + alpha_list)


def command_version(args):
    """Prints the version.

    :param object args: object containing the converted arguments
    """
    print(__version__)


def command_fitness(args):
    """Calculates the fitness for a given language and text

    :param object args: object containing the converted arguments
    """
    quadgram_file = pathlib.Path(quadgram_dir) / (args.lang + ".json")
    with open(str(quadgram_file)) as fh:
        breaker = Breaker(fh)
    if args.text is not None:
        fitness = breaker.calc_fitness(args.text)
    else:
        with open_file(args.in_file) as fh:
            fitness = breaker.calc_fitness_file(fh)
    print(round(fitness, 2))


def command_break(args):
    """Breaks a substitution cipher

    :param object args: object containing the converted arguments
    """
    if not (1 <= args.max_tries <= 10000):
        args.subparser.error("--max-tries must be in the range 1..10000")
    if not (1 <= args.consolidate <= 30):
        args.subparser.error("--consolidate must be in the range 1..30")
    quadgram_file = pathlib.Path(quadgram_dir) / (args.lang + ".json")
    with open(str(quadgram_file)) as fh:
        breaker = Breaker(fh)
    if args.text is not None:
        text = args.text
    else:
        with open_file(args.in_file) as fh:
            text = fh.read()
    result = breaker.break_cipher(
        text, max_rounds=args.max_tries, consolidate=args.consolidate
    )
    print("Alphabet: {}".format(result.alphabet))
    print("Key:      {}".format(result.key))
    print("Fitness: {}".format(round(result.fitness, 2)))
    print("Nbr keys tried: {}".format(result.nbr_keys))
    print("Keys per second: {}".format(round(result.keys_per_second)))
    print("Execution time (seconds): {}".format(round(result.seconds, 3)))
    print("Plaintext:")
    print(result.plaintext)


def command_info(args):
    quadgram_file = pathlib.Path(quadgram_dir) / (args.lang + ".json")
    with open(str(quadgram_file)) as fh:
        breaker = Breaker(fh)
    print("Quadgram file: {}".format(str(quadgram_file.resolve())))
    print("Alphabet: {}".format(breaker.info.alphabet))
    print("Length of alphabet: {}".format(len(breaker.info.alphabet)))
    print("Number of quagrams: {}".format(breaker.info.nbr_quadgrams))
    print("Most frequent quadgram: {}".format(breaker.info.most_frequent_quadgram))
    print("Fitness for most frequent quadgram: {}".format(breaker.info.max_fitness))
    print("Fitness for random text: {}".format(round(breaker.info.average_fitness, 2)))


def command_decode(args):
    """Decodes a substitution cipher with a given key

    :param object args: object containing the arguments from the command line
    """
    if args.key is not None:
        key_str = args.key
    else:
        # keyword given
        key_str = build_key_from_keyword(args)

    alphabet, key_str = consistency_check(args, args.alphabet, key_str)

    key = Key(key_str, alphabet)
    if args.text is not None:
        print(key.decode(args.text))
    else:
        with open_file(args.in_file) as ciphertext_fh, open_file(
            args.out_file, "w"
        ) as plaintext_fh:
            key.decode_file(ciphertext_fh, plaintext_fh)


def command_encode(args):
    """Encodes a substitution cipher with a given key

    :param object args: object containing the arguments from the command line
    """
    if args.random:
        key_list = list(args.alphabet)
        random.shuffle(key_list)
        key_str = "".join(key_list)
    elif args.key is not None:
        key_str = args.key
    else:
        # keyword given
        key_str = build_key_from_keyword(args)

    alphabet, key_str = consistency_check(args, args.alphabet, key_str)

    if args.random:
        print(key_str, file=sys.stderr)
    key = Key(key_str, args.alphabet)
    if args.text is not None:
        print(key.encode(args.text))
    else:
        with open_file(args.in_file) as plaintext_fh, open_file(
            args.out_file, "w"
        ) as ciphertext_fh:
            key.encode_file(plaintext_fh, ciphertext_fh)


def command_quadgrams(args):
    """Creates the quadgrams

    :param object args: object containing the converted arguments
    """
    with open_file(args.corpus) as inp_fh, open_file(args.quadgrams, "w") as outp_fh:
        Breaker.generate_quadgrams(inp_fh, outp_fh, args.alphabet)


def args_add_text_or_in_file(parser, arg_name):
    """Adds the mutual exclusive arguments text and input-file to the parser

    :param parser: parser object to extend with the parameters
    :type parser: object returned by add_parser
    :param str arg_name: the name of the argument, used for the file,
        e.g., "--ciphertext"
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--text",
        metavar="<string>",
        help=(
            "string containing the input text. Note, that line breaks and blanks "
            "might require shell escaping."
        ),
    )
    group.add_argument(
        arg_name,
        dest="in_file",
        metavar="<path>",
        help=(
            "name of the file containing the input text. If neither --text nor "
            "{} is given, the text will be read from STDIN.".format(arg_name)
        ),
    )


def args_add_out_file(parser, arg_name):
    """Adds the argument for the output file to the parser

    :param parser: parser object to extend with the parameters
    :type parser: object returned by add_parser
    :param str arg_name: the name of the argument, used for the file,
        e.g., "--ciphertext"
    """
    parser.add_argument(
        arg_name,
        dest="out_file",
        metavar="<path>",
        help=(
            "file the output is written to. If it is not given, the output is printed "
            "to STDOUT."
        ),
    )


def args_add_key_alternatives(parser, random=False):
    """Add the parameter "--key" to the argparser

    :param parser: parsers object to extend with the key parameter
    :type parsers: object returned by add_subparsers
    :param bool required: indicates if --key is a mandatory parameter
    """
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--key",
        metavar="<string>",
        help=(
            "key containing all characters from the alphabet. The key can be specified "
            "case insensitive, may not contain any non-alphabetical characters, "
            "and every character of the alphabet must be present exactly once."
        ),
        default=None,
    )
    group.add_argument(
        "--keyword",
        metavar="<string>",
        help=(
            "a case-insensitive keyword used to build the key. The key is created by "
            "writing out the keyword, removing repeated letters in it, then writing "
            "all the remaining letters in the alphabet in the usual order. E.g., the "
            'keyword "ZEBRAS" leads to the key "zebrascdfghijklmnopqtuvwxy".'
        ),
        default=None,
    )
    if random:
        group.add_argument(
            "--random",
            action="store_true",
            default=False,
            help=(
                "use a random key by shuffling the alphabet. The key is printed to "
                "STDERR."
            ),
        )


def args_add_alphabet(parser):
    """Add the parameter "--alphabet" to the argparser

    :param parser: parsers object to extend with the key parameter
    :type parsers: object returned by add_subparsers
    """
    parser.add_argument(
        "--alphabet",
        metavar="<string>",
        help=(
            "a string of characters which build the alphabet. Lower and upper "
            "characters are treated the same. By default, 'abcdefghijklmnopqrstuvwxyz' "
            "is used, but any character is allowed (including the blank and e.g., "
            "umlauts). The length of the alphabet may not exceed 32 characters."
        ),
        default="abcdefghijklmnopqrstuvwxyz",
    )


def args_add_language(parser):
    """Add the parameter "--lang" to the argparser

    :param parser: parsers object to extend with the key parameter
    :type parsers: object returned by add_subparsers
    """
    languages = [file_name.stem for file_name in quadgram_dir.glob("*.json")]
    lang_str = "{" + "|".join(languages) + "}"
    parser.add_argument(
        "--lang",
        metavar=lang_str,
        help="language of the text. The default is EN for English.",
        type=str,
        default="EN",
    )


def args_break(subparsers):
    """Defines the arguments for the subcommand "break"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_break = subparsers.add_parser("break", help="break a substitution cipher")
    parser_break.set_defaults(subparser=parser_break, func=command_break)
    args_add_language(parser_break)
    args_add_text_or_in_file(parser_break, "--ciphertext")
    parser_break.add_argument(
        "--consolidate",
        metavar="<int>",
        type=int,
        help=(
            "how often the same key must be found before it is regarded as the best "
            "solution. Default is 3. Lower values provide faster but unreliable "
            "results. If unsure don't touch it."
        ),
        default=3,
    )
    parser_break.add_argument(
        "--max-tries",
        metavar="<int>",
        type=int,
        help=(
            "the maximum number of hill climbings attempts. If no solution is found "
            "before this value is reached the best solution so far will be provided."
        ),
        default=1000,
    )


def args_decode(subparsers):
    """Defines the arguments for the subcommand "decode"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_decode = subparsers.add_parser(
        "decode", help="decode a substitution cipher with a given key"
    )
    parser_decode.set_defaults(subparser=parser_decode, func=command_decode)
    args_add_key_alternatives(parser_decode)
    args_add_alphabet(parser_decode)
    args_add_text_or_in_file(parser_decode, "--ciphertext")
    args_add_out_file(parser_decode, "--plaintext")


def args_encode(subparsers):
    """Defines the arguments for the subcommand "decode"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_encode = subparsers.add_parser(
        "encode", help="encode a plaintext with a given key"
    )
    parser_encode.set_defaults(subparser=parser_encode, func=command_encode)
    args_add_key_alternatives(parser_encode, random=True)
    args_add_alphabet(parser_encode)
    args_add_text_or_in_file(parser_encode, "--plaintext")
    args_add_out_file(parser_encode, "--ciphertext")


def args_fitness(subparsers):
    """Defines the arguments for the subcommand "fitness"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_fitness = subparsers.add_parser(
        "fitness", help="calculate the fitness for a given plaintext"
    )
    parser_fitness.set_defaults(subparser=parser_fitness, func=command_fitness)
    args_add_language(parser_fitness)
    args_add_text_or_in_file(parser_fitness, "--plaintext")


def args_quadgrams(subparsers):
    """Defines the arguments for the subcommand "quadgrams"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_quadgrams = subparsers.add_parser(
        "quadgrams", help="create quadgrams from a given text corpus"
    )
    parser_quadgrams.set_defaults(subparser=parser_quadgrams, func=command_quadgrams)
    args_add_alphabet(parser_quadgrams)
    parser_quadgrams.add_argument(
        "--corpus",
        metavar="<path>",
        help=(
            "The file name of the text corpus file. Only characters from the alphabet"
            "are considered (case insensitive). If this parameter is not provided,"
            "the text corpus will be read from STDIN."
        ),
        default=None,
    )
    parser_quadgrams.add_argument(
        "--quadgrams",
        metavar="<path>",
        help=(
            "The name of the file where the generated quadgrams are stored. "
            "The provided format is JSON. If this parameter is not provided, the "
            "quadgrams will be printed to STDOUT."
        ),
        default=None,
    )


def args_info(subparsers):
    """Defines the arguments for the subcommand "info"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_info = subparsers.add_parser(
        "info", help="print various information about the quadgram file"
    )
    parser_info.set_defaults(subparser=parser_info, func=command_info)
    args_add_language(parser_info)


def args_version(subparsers):
    """Defines the arguments for the subcommand "version"

    :param subparsers: subparsers object to extend with the subcommand
    :type subparsers: object returned by add_subparsers
    """
    parser_version = subparsers.add_parser(
        "version", help="print the version of the tool"
    )
    parser_version.set_defaults(subparser=parser_version, func=command_version)


def build_parser():
    """Creates the parser object

    :return: the parser object as created with argparse
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser(
        description="A collection of tools to work with substitution ciphers"
    )
    subparsers = parser.add_subparsers(help="subcommands to execute", dest="command",)

    args_break(subparsers)
    args_decode(subparsers)
    args_encode(subparsers)
    args_fitness(subparsers)
    args_quadgrams(subparsers)
    args_info(subparsers)
    args_version(subparsers)
    return parser


def main():
    """The entry point for the command line interface
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        args.func(args)
