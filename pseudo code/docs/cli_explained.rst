
CLI by Example
==============

The CLI ``subbreaker`` provides several functions which are described hereafter
in detail. For a more information refer to :ref:`CLI_Reference_Documentation`.

Alphabet and Key
----------------

A central aspect for a substitution cipher is the alphabet and the key.  The
alphabet specifies which characters are to be considered for the substitution,
while the key determines how the characters of the alphabet are substituted.
For encryption each character of the plaintext - if present in the alphabet -
is replaced by the corresponding character of the key. The first character of
the alphabet corresponds to the first character of the key, the second ... (I
think you get the point).

The ``subbreaker`` treats both, the alphabet and the key case-insensitive.
I.e., both can be specified in upper or lower cases (or any mix of both).
However, when performing the substitution the case of the character being
replaced is maintained.

   :Example:

   ::

      Alphabet: abcdefghijklmnopqrstuvwxyz
      Key:      zebrascdfghijklmnopqtuvwxy

The plaintext ``Hello 123 CamelCase`` will result in the ciphertext ``Daiil 123
BzjaiBzpa``. Characters not present in the alphabet will be maintained
unchanged.

The following restrictions apply:

- each character of the alphabet and the key must be unique.
- the key must consist of the same set of characters than the alphabet, and the
  length must be the same.

By default, the alphabet ``abcdefghijklmnopqrstuvwxyz`` is used.

There is no restriction on the characters which can be used in the alphabet and
the key. Thus, ``абвгдежзиклмнопрстуфхцчшэюя012!?`` is a perfectly valid
alphabet.

When breaking a cipher or scoring a cleartext the length of the alphabet and
the key is restricted: Both may not be longer than 32 characters.

.. _cli_transcoding:

Encoding and decoding
---------------------

Encoding a text...

   :Example:

   .. code-block:: console

      $ subbreaker encode --key wisdomabcefghjklnpqrtuvxyz --text \
      > "The trouble with having an open mind, of course, is that people
      > will insist on coming along and trying to put things in it.
      > -- Terry Pratchett"
      Rbo rpktigo vcrb bwucja wj kloj hcjd, km sktpqo, cq rbwr loklgo
      vcgg cjqcqr kj skhcja wgkja wjd rpycja rk ltr rbcjaq cj cr.
      -- Roppy Lpwrsborr

...and decoding it

   :Example:

   .. code-block:: console

      $ subbreaker decode --key wisdomabcefghjklnpqrtuvxyz --text \
      > "Rbo rpktigo vcrb bwucja wj kloj hcjd, km sktpqo, cq rbwr loklgo
      > vcgg cjqcqr kj skhcja wgkja wjd rpycja rk ltr rbcjaq cj cr.
      > -- Roppy Lpwrsborr"
      The trouble with having an open mind, of course, is that people
      will insist on coming along and trying to put things in it.
      -- Terry Pratchett

Cyrillic works as well:

   :Example:

   .. code-block:: console

      $ subbreaker encode --random --alphabet абвгдежзиклмнопрстуфхцчшэюя --text \
      > "«Золотой век» распространения славянской письменности относится ко времени
      > царствования в Болгарии царя Симеона Великого (893—927 гг.), сына царя Бориса.
      > Позже старославянский язык проникает в Сербию, а в конце X века становится
      > языком церкви в Древней Руси."
      ацбглинвятжехэфчкпзмоюшрдсу
      «Вэжэпэй бит» чакфчэкпчахихяу кжабухктэй фякьеиххэкпя эпхэкяпку тэ бчиеихя
      юачкпбэбахяу б Цэжгачяя юачу Кяеиэха Бижятэгэ (893—927 гг.), кыха юачу Цэчяка.
      Фэвни кпачэкжабухктяй увыт фчэхятаип б Кичцяс, а б тэхюи X бита кпахэбяпку
      увытэе юичтбя б Лчибхий Чзкя.

.. note::

   The randomly created key ``ацбглинвятжехэфчкпзмоюшрдсу`` from the example
   above is printed to STDERR.

The ``subbreaker`` supports reading from and writing to files as well:

   :Example:

   .. code-block:: console

      $ echo "The Cyrillic script (/sɪˈrɪlɪk/) is a writing system used for various
      > languages across Eurasia and is used as the national script in various Slavic-,
      > Turkic- and Persian-speaking countries in Eastern Europe, the Caucasus,
      > Central Asia, and Northern Asia." > /tmp/plaintext.txt
      $ subbreaker encode --keyword secret --plaintext /tmp/plaintext.txt --ciphertext /tmp/ciphertext.txt
      $ cat /tmp/ciphertext.txt
      Qdt Cyofiifc pcofmq (/pɪˈoɪiɪh/) fp s wofqfkb pypqtj uptr alo vsoflup
      iskbusbtp scolpp Tuospfs skr fp uptr sp qdt ksqflksi pcofmq fk vsoflup Pisvfc-,
      Quohfc- skr Mtopfsk-pmtshfkb clukqoftp fk Tspqtok Tuolmt, qdt Csucspup,
      Ctkqosi Spfs, skr Kloqdtok Spfs.

The python API for these functions is described here: :ref:`py_transcoding`.

.. _cli_breaking:

Breaking ciphers
----------------

For breaking a substitution cipher without knowing the key the language of the
plaintext must be specified. Based on the language the substitution breaker
knows which alphabet to use and uses statistical material for assessing
resulting plaintexts. Therefore the only other remaining input required is the
ciphertext. Like for the encode and decode subcommands the ciphertext can be
given as a string or as file name containing the ciphertext.

In the basic setup only English is supported, but other languages can be
plugged in easily as well.

If no language is specified, English is used as a default.

Breaking a ciphertext without knowing the key:

   :Example:

   .. code-block:: console

      $ subbreaker break --text "Skp auftrdsth uyuq, hkkg skp rcu bkko dj
      > krcupq; skp auftrdsth hdlq, qlufg kjhy wkpoq ks gdjojuqq; fjo skp
      > lkdqu, wfhg wdrc rcu gjkwhuobu rcfr ykt fpu juvup fhkju. Ftopuy Culatpj"
      Alphabet: abcdefghijklmnopqrstuvwxyz
      Key:      faiousbcdmghxjklepqrtvwzyn
      Fitness: 96.75
      Nbr keys tried: 20475
      Keys per second: 47772
      Execution time (seconds): 0.429
      Plaintext:
      For beautiful eyes, look for the good in
      others; for beautiful lips, speak only words of kindness; and for
      poise, walk with the knowledge that you are never alone. Audrey Hepburn

The fitness reported is a measure how close the resulting plaintext comes to
the given language. Roughly speaking, values close around 100 indicate that the
text is probably readable. Rough overview of typical fitness ranges:

    - 0..95: cleartext is probably not readable
    - 95..105: cleartext probably readable
    - above 105: again, the cleartext is probably not readable, the given
      ciphertext might be too short.

The substitution breaker provides a subcommand to calculate the fitness for any
given text:

    :Example:

    .. code-block:: console

        $ subbreaker fitness --text "The kinges hem wenten and hi seghen the sterre thet
        > yede bifore hem, alwat hi kam over tho huse war ure loverd was; and alswo hi
        > hedden i-fonden ure loverd, swo hin an-urede, and him offrede hire offrendes,
        > gold, and stor, and mirre. Tho nicht efter thet aperede an ongel of hevene in
        > here slepe ine metinge, and hem seide and het, thet hi ne solde ayen wende be
        > herodes, ac be an other weye wende into hire londes."
        92.81

Obviously, the given plaintext is not modern English, indeed it is a Kentish
dialect from the middle age. Therefore the fitness is somewhat below 100.

Refer to :ref:`py_breaking` for the documentation of the related python API.

.. _cli_add_language:

Adding more languages
---------------------

Let's have a look how the substitution breaker can be extended by another
language. To make this task a little bit more challenging, we will use the
Russian language with the Cyrillic alphabet. All we need is a sufficiently huge
text corpus which will be used to extract the statistical characteristics of
the language.

A text corpus is a huge collection of text for a given language, and "they are
used to do statistical analysis and hypothesis testing, checking occurrences or
validating linguistic rules within a specific language territory." (Source:
`Wikipedia, Text corpus`_)

A good resource for text corpora for a variety of languages can be found at the
`University of Leipzig`_ (by the way, my favorite language is `Pfaelzisch`_).

Let's suppose we have found a text corpus and it has been downloaded to the
file ``/tmp/russian_corpus.txt``.

Next we will use the subcommand ``info`` for the English language to find out
the directory where we have to put the statistics file (so called *quadgram
file*) that will be generated from the text corpus.

    :Example:

    .. code-block:: console

        $ subbreaker info --lang EN
        Quadgram file: /home/jens/project/SubstitutionBreaker/subbreaker/quadgram/EN.json
        Alphabet: abcdefghijklmnopqrstuvwxyz
        Length of alphabet: 26
        Number of quagrams: 93609337
        Most frequent quadgram: tion
        Fitness for most frequent quadgram: 135.8
        Fitness for random text: 21.48
        The next step is to find out in which directory the

The line starting with ``Quadgram file:`` tells us where the quadgram files
reside. These are simply JSON files ending with ``.json``. On the CLI the file
names without the extension is used as arguments for the ``--lang`` parameter.

Now let's generate generate the JSON file for Russian:

    :Example:

    .. code-block:: console

        $ subbreaker quadgrams --alphabet абвгдежзиклмнопрстуфхцчшэюя \
          --corpus /tmp/russian_corpus.txt --quadgrams \
          /home/jens/project/SubstitutionBreaker/subbreaker/quadgram/RU.json

This command may take a while, but once it finished: we are done!

Let's check if Russian is now supported:

    :Example:

    .. code-block:: console

        $ subbreaker break --help
        usage: subbreaker break [-h] [--lang {RU|EN}]
                                [--text <string> | --ciphertext <path>]
                                [--consolidate <int>] [--max-tries <int>]

        optional arguments:
          -h, --help           show this help message and exit
          --lang {RU|EN}       language of the text. The default is EN for English.
          --text <string>      string containing the input text. Note, that line
                               breaks and blanks might require shell escaping.
          --ciphertext <path>  name of the file containing the input text. If neither
                               --text nor --ciphertext is given, the text will be read
                               from STDIN.
          --consolidate <int>  how often the same key must be found before it is
                               regarded as the best solution. Default is 3. Lower
                               values provide faster but unreliable results. If unsure
                               don't touch it.
          --max-tries <int>    the maximum number of hill climbings attempts. If no
                               solution is found before this value is reached the best
                               solution so far will be provided.

Yes! The language parameter ``--lang`` is extended by ``RU``. Let's check some
more information regarding the newly supported language:

    :Example:

    .. code-block:: console

        $ subbreaker info --lang RU
        Quadgram file: /home/jens/project/SubstitutionBreaker/subbreaker/quadgram/RU.json
        Alphabet: абвгдежзиклмнопрстуфхцчшэюя
        Length of alphabet: 27
        Number of quagrams: 81540022
        Most frequent quadgram: ения
        Fitness for most frequent quadgram: 134.9
        Fitness for random text: 25.99

So, more than 81 million letters of the text corpus were processed. Note, that
letters not present in the alphabet have been ignored. There are some
additional data provided, which are not covered here (hey, they are self
explaining, aren't they?).

Now let's see if we can crack the cipher we used in an example above:

    :Example:

    .. code-block:: console

      $ subbreaker break --lang RU --text "«Вэжэпэй бит» чакфчэкпчахихяу
      > кжабухктэй фякьеиххэкпя эпхэкяпку тэ бчиеихя юачкпбэбахяу б Цэжгачяя юачу
      > Кяеиэха Бижятэгэ (893—927 гг.), кыха юачу Цэчяка.  Фэвни кпачэкжабухктяй
      > увыт фчэхятаип б Кичцяс, а б тэхюи X бита кпахэбяпку увытэе юичтбя б
      > Лчибхий Чзкя."
      Alphabet: абвгдежзиклмнопрстуфхцчшэюя
      Key:      албгцинвятжехэфчкпздшюсомру
      Fitness: 101.83
      Nbr keys tried: 186030
      Keys per second: 37320
      Execution time (seconds): 4.985
      Plaintext:
      «Золотой век» распространения
      славянской письменности относится ко времени царствования в Долгарии царя
      Симеона Великого (893—927 гг.), сына царя Дориса.  Позже старославянский
      язык проникает в Сердич, а в конце X века становится языком церкви в
      Бревней Руси.

For me these are all hieroglyphs, but I believe the result is rather good (it
looks like one single character is not correct). Anyway, this example
demonstrated the power of this tool.

Refer to :ref:`py_add_language` for the documentation of the related python
API.

.. _`University of Leipzig`: https://cls.corpora.uni-leipzig.de

.. _`Pfaelzisch`: https://cls.corpora.uni-leipzig.de/de?corpusLanguage=pfl#tblselect

.. _`Wikipedia, Text corpus`: https://en.wikipedia.org/wiki/Text_corpus
