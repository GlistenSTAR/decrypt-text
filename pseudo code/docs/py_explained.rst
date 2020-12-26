
Python by Example
=================

This chapter shows how to use the python classes provided by the ``subbreaker``
package.

.. _py_transcoding:

Encoding and decoding
---------------------

For en- and decoding the class :class:`subbreaker.Key` is used.

Very basic encoding:

::

    >>> import subbreaker
    >>> key = subbreaker.Key("zebrascdfghijklmnopqtuvwxy")
    >>> key.encode("This is a secret message!")
    'Qdfp fp z paboaq jappzca!'

Using a non-default alphabet:

::

    >>> key_cyrillic = subbreaker.Key("ацбглинвятжехэфчкпзмоюшрдсу", alphabet="абвгдежзиклмнопрстуфхцчшэюя")
    >>> key_cyrillic.encode("«Золотой век» распространения славянской")
    '«Вэжэпэй бит» чакфчэкпчахихяу кжабухктэй'

And now decoding:

::

    >>> key.decode("Qdfp fp z paboaq jappzca!")
    'This is a secret message!'

Encoding and decoding works as well with file-like objects:

::

    >>> import io
    >>> plaintext_fh = io.StringIO("This is a secret message!")
    >>> ciphertext_fh = io.StringIO()
    >>> key.encode_file(plaintext_fh=plaintext_fh, ciphertext_fh=ciphertext_fh)
    >>> ciphertext_fh.getvalue()
    'Qdfp fp z paboaq jappzca!'
    >>> plaintext_fh = io.StringIO()
    >>> key.decode_file(ciphertext_fh=ciphertext_fh, plaintext_fh=plaintext_fh)
    >>> plaintext_fh.getvalue()
    'This is a secret message!'

All these operations are supported by the CLI as well, refer to
:ref:`cli_transcoding`.

.. _py_breaking:

Breaking ciphers
----------------

Breaking substitution ciphers requires the use of the
:class:`subbreaker.Breaker` class. For more information refer to .

For instantiating a Breaker object, the file handle to a quadgram file must be
given.

::

    >>> ciphertext = """Skp auftrdsth uyuq, hkkg skp rcu bkko dj
    ... krcupq; skp auftrdsth hdlq, qlufg kjhy wkpoq ks gdjojuqq; fjo skp
    ... lkdqu, wfhg wdrc rcu gjkwhuobu rcfr ykt fpu juvup fhkju. Ftopuy Culatpj"""
    >>> with open("/home/jens/project/SubstitutionBreaker/subbreaker/quadgram/EN.json") as fh:
    ...     breaker = subbreaker.Breaker(fh)
    ...

Information about the loaded quadgram file is provided by the ``info``
property, which represents a :class:`subbreaker.BreakerInfo` object.

::

    >>> breaker.info
    <subbreaker.breaker.BreakerInfo object at 0x7f070b99b810>
    >>> vars(breaker.info)
    {'alphabet': 'abcdefghijklmnopqrstuvwxyz', 'nbr_quadgrams': 93609337, 'most_frequent_quadgram': 'tion', 'average_fitness': 21.48411689016491, 'max_fitness': 135.8}

The method ``break_cipher`` returns a :class:`subbreaker.BreakerResult` object.

::

    >>> result = breaker.break_cipher(ciphertext)
    >>> result
    <subbreaker.breaker.BreakerResult object at 0x7f01a3626c10>
    >>> print(result.plaintext)
    For beautiful eyes, look for the good in
    others; for beautiful lips, speak only words of kindness; and for
    poise, walk with the knowledge that you are never alone. Audrey Hepburn
    >>> print(result.ciphertext)
    Skp auftrdsth uyuq, hkkg skp rcu bkko dj
    krcupq; skp auftrdsth hdlq, qlufg kjhy wkpoq ks gdjojuqq; fjo skp
    lkdqu, wfhg wdrc rcu gjkwhuobu rcfr ykt fpu juvup fhkju. Ftopuy Culatpj
    >>> result.key
    'faxousbcdzghejklnpqrtvwmyi'
    >>> result.alphabet
    'abcdefghijklmnopqrstuvwxyz'
    >>> result.fitness
    967.4892086330935
    >>> result.nbr_keys
    36075
    >>> result.nbr_rounds
    22
    >>> result.keys_per_second
    50509.61
    >>> result.seconds
    0.7142205238342285

Additionally, a :class:`subbreaker.Key` object is provided by the Breaker class
which allows to encode/decode texts with the broken key directly.

::

    >>> breaker.key
    <subbreaker.key.Key object at 0x7f01a3626e10>
    >>> breaker.key.encode("Hey, this is encoded with the broken key!")
    'Cuy, rcdq dq ujxkouo wdrc rcu apkguj guy!'

Breaking substitutions ciphers is supported by the CLI as well, refer to
:ref:`cli_breaking`.

Calculating the fitness for a given text:

::

    >>> breaker.calc_fitness("Hey, this is encoded with the broken key!")
    99.1103448275862

.. _py_add_language:

Adding a new language
---------------------

The static method :func:`subbreaker.Breaker.generate_quadgrams` is used. The
method takes the file handles to the corpus and the quadgram file as input, as
well as the alphabet:

::

    >>> with open("/tmp/rus.txt") as corpus_fh, open("/tmp/rus.json", "w") as quadgram_fh:
    ...     subbreaker.Breaker.generate_quadgrams(corpus_fh, quadgram_fh, alphabet="абвгдежзиклмнопрстуфхцчшэюя")
    ...

Now let's use the new language:

::

    >>> with open("/tmp/rus.json") as fh:
    ...    breaker_rus = subbreaker.Breaker(fh)
    ...
    >>> result = breaker_rus.break_cipher("""«Вэжэпэй бит» чакфчэкпчахихяу
    ... кжабухктэй фякьеиххэкпя эпхэкяпку тэ бчиеихя юачкпбэбахяу б Цэжгачяя юачу
    ... Кяеиэха Бижятэгэ (893—927 гг.), кыха юачу Цэчяка.  Фэвни кпачэкжабухктяй
    ... увыт фчэхятаип б Кичцяс, а б тэхюи X бита кпахэбяпку увытэе юичтбя б
    ... Лчибхий Чзкя.""")
    >>> result.key
    'агбцлинвятжехэфчкпзршюсомду'
    >>> print(result.plaintext)
    «Золотой век» распространения
    славянской письменности относится ко времени царствования в Голбарии царя
    Симеона Великобо (893—927 бб.), сына царя Гориса.  Позже старославянский
    язык проникает в Сергич, а в конце X века становится языком церкви в
    Древней Руси.

Adding a new language is also supported by the CLI, refer to
:ref:`cli_add_language`.
