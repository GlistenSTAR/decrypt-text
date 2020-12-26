|Build Status| |Coverage| |License| |Black|

Substitution Breaker
####################

This project provides a Python implementation for breaking classical
substitution ciphers.

More documentation of the project including a `detailed description of the CLI
and the python API <https://guballa.gitlab.io/SubstitutionBreaker/cli.html>`_
is available as well.

.. inclusion-marker-start-overview

Overview
========

A `substitution cipher`_ is a method of encryption by which the letters of the
plaintext are systematically replaced by substitute letters. The receiver
deciphers the text by performing an inverse substitution.

The correlation between the letters of the plaintext and the substitute letters
is defined by the key.

Example:

::

   Alphabet: ABCDEFGHIJKLMNOPQRSTUVWXYZ
   Key:      ZEBRASCDFGHIJKLMNOPQTUVWXY

The letter "A" from the plaintext maps to the cipher text "Z", "B" to "E", and
so on. Thus the plaintext "flee at once. we are discovered!" is enciphered as
"siaa zq lkba. va zoa rfpbluaoar!"

This package provides a CLI which supports the following operations:

* encoding and decoding a text with a given key
* breaking a substitution cipher text when the key is unknown (English language)
* tools for adding support for other languages and/or other alphabets

All the features supported by the CLI are exposed through functions and classes
by a Python package.

.. _`substitution cipher`: https://en.wikipedia.org/wiki/Substitution_cipher

.. inclusion-marker-end-overview

.. inclusion-marker-start-installation

Installation
============

This package requires Python3.5 or higher.

The recommended way installing the package is by using `virtual environments`_.
If you decide to follow this recommendation, just execute the following
optional command (adapt the path to the virtual environment according to your
preferences):

.. code-block:: console

   $ mkdir -p ~/.virtualenv/subbreaker \
      && python3 -m venv ~/.virtualenv/subbreaker \
      && source ~/.virtualenv/subbreaker/bin/activate

Next, install the package using pip. If you want to use the latest stable
version of the package , use the command

.. code-block:: console

   $ pip install git+https://gitlab.com/guballa/SubstitutionBreaker.git@master

Or, if you want to use the most recent version from the development branch:

.. code-block:: console

   $ pip install git+https://gitlab.com/guballa/SubstitutionBreaker.git

.. _`virtual environments`: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments

.. inclusion-marker-end-installation

.. inclusion-marker-start-usage

Basic Usage
===========

For a full documentation of the `subbreaker` command refer to the
`documentation here <https://guballa.gitlab.io/SubstitutionBreaker/cli.html>`_.
There you will find also a detailed description how to use the package directly
with Python. In the following only some basic examples for using the CLI are
given.

The command ``subbreaker`` supports several subcommands. To display them type:

.. code-block:: console

   $ subbreaker --help

You can get a detailed help on every subcommand by ``subbreaker <subcommand>
--help``. And here comes `subbreaker` in action:

Encoding a clear text...

.. code-block:: console

   $ subbreaker encode --key ZEBRASCDFGHIJKLMNOPQTUVWXY --text "flee at once. we are discovered!"
   siaa zq lkba. va zoa rfpbluaoar!

...and decoding it back:

.. code-block:: console

   $ subbreaker decode --key ZEBRASCDFGHIJKLMNOPQTUVWXY --text "siaa zq lkba. va zoa rfpbluaoar!"
   flee at once. we are discovered!

Break a cipher without knowing the key:

.. code-block:: console

   $ subbreaker break --lang EN --text \
   "Rbo rpktigo vcrb bwucja wj kloj hcjd, km sktpqo, cq rbwr loklgo
   > vcgg cjqcqr kj skhcja wgkja wjd rpycja rk ltr rbcjaq cj cr.
   > -- Roppy Lpwrsborr"
   Key: wisdomabcznghjklfpqrtuvxye
   Score: 103.68
   Nbr keys tried: 37050
   Keys per second: 61850
   Execution time (seconds): 0.599
   Clear text:
   The trouble with having an open mind, of course, is that people
   will insist on coming along and trying to put things in it.
   -- Terry Pratchett

.. inclusion-marker-end-usage

.. |Build Status| image:: https://gitlab.com/guballa/SubstitutionBreaker/badges/development/pipeline.svg
   :target: https://gitlab.com/guballa/SubstitutionBreaker/-/commits/development

.. |Coverage| image:: https://gitlab.com/guballa/SubstitutionBreaker/badges/development/coverage.svg
   :target: https://gitlab.com/guballa/SubstitutionBreaker/-/commits/development

.. |License| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://gitlab.com/guballa/SubstitutionBreaker/-/blob/development/LICENSE

.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/python/black
