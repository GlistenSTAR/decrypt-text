# -*- coding: utf-8 -*-
"""Basic functions for encoding/decoding substitution ciphers with a given key
"""
import sys


class AlphabetInvalid(Exception):
    """An exception raised when an alphabet is invalid"""
    pass


class KeyInvalid(Exception):
    """An exception raised when a key is invalid"""
    pass


class Key(object):
    """Uses a key and an alphabet for transcoding substitution ciphers.

    The first character of the alphabet corresponds to the first character of the
    key, the second character of the alphabet to the second character of the key,
    and so on. The alphabet can consist of any characters (including e.g.
    umlauts), and the length is variable, i.e., it is not restricted to the 26 letters
    of the alphabet.

    :example:
        ::

            Alphabet: abcdefghijklmnopqrstuvwxyz
            Key:      zebrascdfghijklmnopqtuvwxy

        The letter "a" from the plaintext maps to "z" in the ciphertext, "b" to "e",
        and so on. Thus the plaintext "flee at once. we are discovered!" is enciphered
        as "siaa zq lkba. va zoa rfpbluaoar!"

        This example was taken from
        `Wikipedia <https://en.wikipedia.org/wiki/Substitution_cipher>`_.

    :param str key: The key to use. Must have the same length than alphabet.
        It is case insensitive.
    :param str alphabet: The set of characters which define the alphabet.
        Characters which are not in the alphabet will be ignored when transcoding.
    """

    _DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    def __init__(self, key, alphabet=_DEFAULT_ALPHABET):
        """Instantiate object
        """
        self._alphabet = self.check_alphabet(alphabet)
        self._key = self.check_key(key, self._alphabet)

        camel_key = self._upper(key) + key.lower()
        camel_alphabet = self._upper(alphabet) + alphabet.lower()
        self._encode = str.maketrans(camel_alphabet, camel_key)
        self._decode = str.maketrans(camel_key, camel_alphabet)

    @staticmethod
    def check_alphabet(alphabet):
        """Checks an alphabet for consistency

        Checks, if each character is unique.

        :param str alphabet: the alphabet to check
        :return: the alphabet in normalized form (i.e., in lower cases)
        :rtype: str
        :raises: AlphabetInvalid if the check fails
        """
        alphabet = alphabet.lower()
        if len(alphabet) != len(set(alphabet)):
            raise AlphabetInvalid("alphabet characters must be unique")
        return alphabet

    @staticmethod
    def check_key(key, alphabet):
        """Checks a key for consistency against a given alphabet

        It is assumed that the given alphabet has already been check for consistency
        before. The following checks are performed:

        - the characters in the key must be unique
        - the key must have the same length than the alphabet
        - the set of characters in the key must be the same than the set of characters
          in the alphabet

        :param str key: the key to be validated
        :param str alphabet: the alphabet against which the key is validated
        :return: the validated key in normalized form (i.e., in lower cases)
        :rtype: str
        :raises: KeyInvalid if one of the checks fails
        """
        key = key.lower()
        key_set = set(key)
        if len(key) != len(key_set):
            raise KeyInvalid("key characters must be unique")

        if len(key) != len(alphabet):
            raise KeyInvalid("key must be as long as the alphabet")
        if key_set != set(alphabet):
            raise KeyInvalid(
                "key must use the same set of characters than the alphabet"
            )
        return key

    @staticmethod
    def _upper(string):
        """
        Converts a string to upper case in a safe way

        Reason for this function is the German "ß".
        Problem: "ß".upper() results in "SS" which corrupts the xcoding translation
        table. Therefore in such a case the character is simply taken as it is and
        is not converted.

        :Example:
            "Viele Grüße".upper() results in "VIELE GRÜSSE"
            _upper("Viele Grüße") results in "VIELE GRÜßE"

        :param str string: the string to be converted to upper case
        :return: the string converted to upper case
        :rtype: str
        """
        return "".join(
            [char.upper() if len(char.upper()) == 1 else char for char in string]
        )

    def decode(self, ciphertext):
        """Decodes a ciphertext with the given key into the plaintext

        :param str ciphertext: the ciphertext to decode with the given key
        :return: the resulting plaintext
        :rtype: str
        """
        return ciphertext.translate(self._decode)

    def encode(self, plaintext):
        """Encodes a plaintext with the given key into the ciphertext

        :param str plaintext: the plaintext to encode with the given key
        :return: the resulting ciphertext
        :rtype: str
        """
        return plaintext.translate(self._encode)

    def decode_file(self, ciphertext_fh=sys.stdin, plaintext_fh=sys.stdout):
        """Decodes ciphertext read from the given file handle

        :param ciphertext_fh: the file handle (i.e., a read()-supporting file like
            object) the ciphertext is read from. Defaults to STDIN.
        :type ciphertext_fh: file object
        :param plaintext_fh: the file handle (i.e., a .write()-supporting file like
            object) the resulting plaintext is written to. Defaults to STDOUT.
        :type plaintext_fh: file object
        """
        for line in ciphertext_fh:
            plaintext_fh.write(self.decode(line))

    def encode_file(self, plaintext_fh=sys.stdin, ciphertext_fh=sys.stdout):
        """Encodes plaintext read from the given file handle

        :param plaintext_fh: the file handle (i.e., a read()-supporting file like
            object) the plaintext is read from. Defaults to STDIN.
        :type plaintext_fh: file object
        :param ciphertext_fh: the file handle (i.e., a .write()-supporting file like
            object) the resulting ciphertext is written to. Defaults to STDOUT.
        :type ciphertext_fh: file object
        """
        for line in plaintext_fh:
            ciphertext_fh.write(self.encode(line))
