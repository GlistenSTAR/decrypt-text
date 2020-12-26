# -*- coding: utf-8 -*-
"""This module provides support for breaking substitution ciphers.

This includes generating quadgrams from a text corpus, scoring a plaintext and
breaking substitution ciphers.
"""

import math
import json
import sys
import random
import time

from subbreaker.key import Key, AlphabetInvalid


class BreakerInfo(object):
    """Class representing various information of the quadgrams for a given language

    :ivar str alphabet: text representation of the alphabet
    :ivar int nbr_quadgrams: the number of quadgrams considered for the generated
        quadgram file. This value may be lower than the corpus size as only characters
        from the alphabet are considered for this value
    :ivar str most_frequent_quadgram: the most occurring same sequence of four
        characters within the corpus used to generate the quadgram file. For English,
        the expected value here is "tion".
    :ivar float average_fitness: the expected fitness of a text if all characters are
        generated randomly with the same probability.
    :ivar float max_fitness: the fitness for the most frequent quadgram
    """

    def __init__(
        self,
        alphabet=None,
        nbr_quadgrams=None,
        most_frequent_quadgram=None,
        average_fitness=None,
        max_fitness=None,
    ):
        self.alphabet = alphabet
        self.nbr_quadgrams = nbr_quadgrams
        self.most_frequent_quadgram = most_frequent_quadgram
        self.average_fitness = average_fitness
        self.max_fitness = max_fitness


class BreakerResult(object):
    """Class representing the result for breaking a substitution cipher

    :ivar str ciphertext: the original ciphertext
    :ivar str plaintext: the resulting plaintext using the found key
    :ivar str key: the best key found by the breaker
    :ivar str alphabet: the alphabet used to break the cipher
    :ivar float fitness: the fitness of the resulting plaintext
    :ivar int nbr_keys: the number of keys tried by the breaker
    :ivar nbr_rounds: the number of hill climbings performed, starting with a random
        key
    :ivar float keys_per_second: the number of keys tried per second
    :ivar float seconds: the time in seconds used to break the cipher
    """

    def __init__(
        self,
        ciphertext=None,
        plaintext=None,
        key=None,
        alphabet=None,
        fitness=0,
        nbr_keys=0,
        nbr_rounds=0,
        keys_per_second=0,
        seconds=0,
    ):
        """Instantiation method
        """
        self.ciphertext = ciphertext
        self.plaintext = plaintext
        self.key = key
        self.alphabet = alphabet
        self.fitness = fitness
        self.nbr_keys = nbr_keys
        self.nbr_rounds = nbr_rounds
        self.keys_per_second = keys_per_second
        self.seconds = seconds

    def __str__(self):
        return "key = {}".format(self.key)


class Breaker(object):
    """Class to represent the breaker implementation based on quadgrams

    :ivar info: a :class:`BreakerInfo` object
    :type info: :class:`BreakerInfo` object
    :ivar key: a :class:`Key` object with the key found when breaking a cipher
    :type key: :class:`Key`
    :param quadgram_fh: file handle (i.e., a read()-supporting file like object)
        to read the quadgrams from.
    :type quadgram_fh: file handle
    """

    _DEFAULT_ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    def __init__(self, quadgram_fh):
        """Init the instance
        """
        obj = json.load(quadgram_fh)
        self._alphabet = obj["alphabet"]
        self._alphabet_len = len(self._alphabet)
        self._quadgrams = obj["quadgrams"]
        self.info = BreakerInfo(
            alphabet=obj["alphabet"],
            nbr_quadgrams=obj["nbr_quadgrams"],
            most_frequent_quadgram=obj["most_frequent_quadgram"],
            average_fitness=obj["average_fitness"] / 10,
            max_fitness=obj["max_fitness"] / 10,
        )
        self.key = None

    @staticmethod
    def _file_iterator(file_fh, alphabet):
        """Implements an iterator for a given file based text file

        The iterator will yield all charcters of the text file which are present in
        the alphabet, all other characters will be skipped.

        :param file_fh: the file handle (i.e., a read()-supporting file like object)
            of the text file
        :type file_fh: file handle
        :param str alphabet: the alphabet to apply with this text file.
        :return: an iterator which iterates over all characters of the text file
            which are present in the alphabet.
        """
        trans = {val: key for key, val in enumerate(alphabet.lower())}
        for line in file_fh:
            line = line.lower()
            for char in line:
                val = trans.get(char)
                if val is not None:
                    yield val

    @staticmethod
    def _text_iterator(txt, alphabet):
        """Implements an iterator for a given text string

        The iterator will yield all characters of the text string which are present in
        the alphabet, all other characters will be skipped.

        :param str txt: the text string to process
        :param str alphabet: the alphabet to apply with this text string
        :return: an iterator which iterates over all characters of the text string
            which are present in the alphabet.
        """
        trans = {val: key for key, val in enumerate(alphabet.lower())}
        for char in txt.lower():
            val = trans.get(char)
            if val is not None:
                yield val

    @staticmethod
    def generate_quadgrams(corpus_fh, quadgram_fh, alphabet=_DEFAULT_ALPHABET):
        """Static method to generate quadgrams from a text file

        Based on the text file the quadgrams will be serialized in JSON format into
        the file "quadgram_file".

        The quadgrams will be generated by the following steps:

        - the number of occurrences of the quadgram within the text file is counted
          per quadgram
        - if a quadgram does not occur in the text file (i.e. the counted value
          is zero), it will be set to 1/10th of the least often occurring quadgram. This
          is done to allow calculating the logarithm and avoiding "math domain errors"
        - the logarithm of the number of occurrences for each quadgram is calculated
        - the results are normalized (which is not strictly required, but it provides
          fitness values which can be somehow interpreted by humans)

            - to avoid negative values
            - to have a reference point in such a way that value = 100 corresponds to
              "typical occurrences" of the quadgram in the given language. Values below
              100 indicate "less often occurring quadgrams" (the lower the value the
              lesser it will statistically occur), while values above 100 indicate that
              these quadgrams are occurring more often then average in the given
              language. Is that clear enough?

        The quadgrams as well as the used alphabet is then serialized into a JSON
        structure and store in the file "quadgram_file".

        :param corpus_fh: the file handle (i.e., a read()-supporting file like object)
            of the text corpus file to process
        :type corpus_fh: file handle
        :param str quadgram_fh: the file handle (i.e., a write()-supporting file like
            object) where the quadgrams will be serialized to
        :type quadgram_fh: file handle
        :param str alphabet: the alphabet to apply with this text file.
        :raises: ValueError - if the alphabet has more than 32 characters
        """
        alphabet = Key.check_alphabet(alphabet)
        if len(alphabet) > 32:
            raise AlphabetInvalid("Alphabet must have less or equal than 32 characters")
        iterator = Breaker._file_iterator(corpus_fh, alphabet)
        quadgram_val = iterator.__next__()
        quadgram_val = (quadgram_val << 5) + iterator.__next__()
        quadgram_val = (quadgram_val << 5) + iterator.__next__()
        quadgrams = [0 for cntr in range(32 * 32 * 32 * 32)]
        for numerical_char in iterator:
            quadgram_val = ((quadgram_val & 0x7FFF) << 5) + numerical_char
            quadgrams[quadgram_val] += 1

        quadgram_sum = sum(quadgrams)
        quadgram_min = 10000000
        for val in quadgrams:
            if val:
                quadgram_min = min(quadgram_min, val)
        offset = math.log(quadgram_min / 10 / quadgram_sum)

        norm = 0
        for idx, val in enumerate(quadgrams):
            if val:
                prop = val / quadgram_sum
                new_val = math.log(prop) - offset
                quadgrams[idx] = new_val
                norm += prop * new_val

        for idx, val in enumerate(quadgrams):
            quadgrams[idx] = round(quadgrams[idx] / norm * 1000)

        # Just for curiosity: determine the most frequent quadgram
        max_idx = quadgrams.index(max(quadgrams))
        max_val = quadgrams[max_idx]
        # now construct the ASCII representation from the index
        max_chars = []
        index = max_idx
        for _ in range(4):
            max_chars = [alphabet[index & 0x1F]] + max_chars
            index >>= 5

        json.dump(
            {
                "alphabet": alphabet,
                "nbr_quadgrams": quadgram_sum,
                "most_frequent_quadgram": "".join(max_chars),
                "max_fitness": max_val,
                "average_fitness": sum(quadgrams) / (len(alphabet) ** 4),
                "quadgrams": quadgrams,
            },
            quadgram_fh,
            indent=0,
        )

    def _calc_fitness(self, iterator):
        """Calculate the fitness from the characters provided by the iterator

        :param iterator: iterator which provides the characters relevant for
            calculating the fitness
        :param type: iterator object
        :return: the fitness of the text. A value close to 100 means, the
            text is probably in the same language than the language used to generate
            the quadgrams. The more the value differs from 100, the lesser the
            probability that the examined text corresponds to the quadgram language.
            Lower values indicate more random text, while values significantly
            greater than 100 indicate (nonsense) text with too much frequently used
            quadgrams (e.g., ``tionioningatheling``).
        :rtype: float
        :raises: ValueError
        """
        try:
            quadgram_val = iterator.__next__()
            quadgram_val = (quadgram_val << 5) + iterator.__next__()
            quadgram_val = (quadgram_val << 5) + iterator.__next__()
        except StopIteration:
            raise ValueError(
                "More than three characters from the given alphabet are required"
            )

        fitness = 0
        nbr_quadgrams = 0
        quadgrams = self._quadgrams
        for numerical_char in iterator:
            quadgram_val = ((quadgram_val & 0x7FFF) << 5) + numerical_char
            fitness += quadgrams[quadgram_val]
            nbr_quadgrams += 1
        if nbr_quadgrams == 0:
            raise ValueError(
                "More than three characters from the given alphabet are required"
            )
        return fitness / nbr_quadgrams / 10

    def calc_fitness_file(self, cleartext_fh=sys.stdin):
        """Method to calculate the fitness of the given file contents

        :param cleartext_fh: the file handle (i.e., a read()-supporting file like
            object) from which the fitness will be calculated
        :type cleartext_fh: file handle
        :return: the fitness of the text. A value close to 100 means, the
            text is probably in the same language than the language used to generate
            the quadgrams. The more the value differs from 100, the lesser the
            probability that the examined text corresponds to the quadgram language.
            Lower values indicate more random text, while values significantly
            greater than 100 indicate (nonsense) text with too much frequently used
            quadgrams (e.g., ``tionioningatheling``).
        :rtype: float
        """
        return self._calc_fitness(Breaker._file_iterator(cleartext_fh, self._alphabet))

    def calc_fitness(self, txt):
        """Method to calculate the fitness for the given text string

        :param str txt: the text string for which the fitness shall be determined
        :return: the fitness of the text. A value close to 100 means, the
            text is probably in the same language than the language used to generate
            the quadgrams. The more the value differs from 100, the lesser the
            probability that the examined text corresponds to the quadgram language.
            Lower values indicate more random text, while values significantly
            greater than 100 indicate (nonsense) text with too much frequently used
            quadgrams (e.g., ``tionioningatheling``).
        :rtype: float
        """
        return self._calc_fitness(Breaker._text_iterator(txt, self._alphabet))

    def _hill_climbing(self, key, cipher_bin, char_positions):
        """Basic hill climbing function

        Starting from the given key two charters are swapped, hoping the mutated key
        provides a better result than the original key. This is done for all possible
        pairs of characters. If a better key is found, the mutation process starts
        over again. If no better key is found, we reached a (local) maximum and the
        fitness and the number of keys is returned.

        :param key: the key to start with. The key is represented as a list where each
            character is represented by an integer 0..25 (for the default alphabet).
            0 corresponds to the first character of the alphabet, 1 to the second,
            etc.
        :type key: list(int)
        :param cipher_bin: the ciphertext in binary representation, i.e. each
            character present in the alphabet is represented as an integer.
        :type cipher_bin: list(int)
        :param char_positions: a list for each character of the alphabet indicating
            at which positions it is occurring. The positions are stored in a list.
            Used to quickly update the plaintext when two characters of the key are
            swapped.
        :type char_positions: list(list(int))
        which for each character holds a list where in
            the ciphertext it occurs.
        :return: tuple of the max_fitness and the number of keys evaluated
        :rtype: tuple
        """
        plaintext = [key.index(idx) for idx in cipher_bin]
        quadgram = self._quadgrams
        key_len = self._alphabet_len
        nbr_keys = 0
        max_fitness = 0
        better_key = True
        while better_key:
            better_key = False
            for idx1 in range(key_len - 1):
                for idx2 in range(idx1 + 1, key_len):
                    ch1 = key[idx1]
                    ch2 = key[idx2]
                    for idx in char_positions[ch1]:
                        plaintext[idx] = idx2
                    for idx in char_positions[ch2]:
                        plaintext[idx] = idx1
                    nbr_keys += 1
                    tmp_fitness = 0
                    quad_idx = (plaintext[0] << 10) + (plaintext[1] << 5) + plaintext[2]
                    for char in plaintext[3:]:
                        quad_idx = ((quad_idx & 0x7FFF) << 5) + char
                        tmp_fitness += quadgram[quad_idx]
                    if tmp_fitness > max_fitness:
                        max_fitness = tmp_fitness
                        better_key = True
                        key[idx1] = ch2
                        key[idx2] = ch1
                    else:
                        for idx in char_positions[ch1]:
                            plaintext[idx] = idx1
                        for idx in char_positions[ch2]:
                            plaintext[idx] = idx2
        return max_fitness, nbr_keys

    def break_cipher(self, ciphertext, max_rounds=10000, consolidate=3):
        """Breaks a given cipher text

        :param str ciphertext: the ciphertext to break
        :param int max_rounds: the maximum of hill climbing rounds to execute
        :param int consolidate: the number of times the best local maximum must be
            reached before it is considers the overall best solution
        :return: an BreakerResult object
        :rtype: :class:`BreakerResult`
        """
        if not (1 <= max_rounds <= 10000):
            raise ValueError("maximum number of rounds not in the valid range 1..10000")
        if not (1 <= consolidate <= 30):
            raise ValueError("consolidate parameter out of valid range 1..30")
        start_time = time.time()
        nbr_keys = 0
        cipher_bin = [
            char for char in Breaker._text_iterator(ciphertext, self._alphabet)
        ]
        if len(cipher_bin) < 4:
            raise ValueError("ciphertext is too short")

        char_positions = []
        for idx in range(len(self._alphabet)):
            char_positions.append([i for i, x in enumerate(cipher_bin) if x == idx])

        key_len = len(self._alphabet)
        local_maximum, local_maximum_hit = 0, 1
        key = [idx for idx in range(key_len)]
        best_key = key.copy()
        for round_cntr in range(max_rounds):
            random.shuffle(key)
            fitness, tmp_nbr_keys = self._hill_climbing(key, cipher_bin, char_positions)
            nbr_keys += tmp_nbr_keys
            if fitness > local_maximum:
                local_maximum = fitness
                local_maximum_hit = 1
                best_key = key.copy()
            elif fitness == local_maximum:
                local_maximum_hit += 1
                if local_maximum_hit == consolidate:
                    break
        key_str = "".join([self._alphabet[x] for x in best_key])
        self.key = Key(key_str, alphabet=self._alphabet)
        seconds = time.time() - start_time
        return BreakerResult(
            ciphertext=ciphertext,
            plaintext=self.key.decode(ciphertext),
            key=key_str,
            alphabet=self._alphabet,
            fitness=local_maximum / (len(cipher_bin) - 3) / 10,
            nbr_keys=nbr_keys,
            nbr_rounds=round_cntr,
            keys_per_second=round(nbr_keys / seconds, 3),
            seconds=seconds,
        )
