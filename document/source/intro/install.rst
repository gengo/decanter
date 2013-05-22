.. index::
   single: install

===================
Quick install guide
===================

Before you can use decanter, you'll need to get it installed.

Install decanter
================

You've got two easy options to install decanter:

* Install an `official release`_
* Install the latest `development version`_


Official release
----------------
`Please wait <https://github.com/gengo/decanter/issues/19>`_

Development version
-------------------

You have the option to use Git or Zip

* Use git

- ::

    git clone https://github.com/gengo/decanter.git

* Download zip

- ::

    wget -qO- -O decanter.zip https://github.com/gengo/decanter/archive/master.zip && unzip decanter.zip && rm decanter.zip && mv decanter-master decanter

You should end up with a directory structure like this:

::

    decanter/
    ├── LICENSE.txt
    ├── MANIFEST.in
    ├── README.md
    ├── decanter
    ├── document
    ├── requirements.txt
    ├── setup.py
    ├── test_runner.py
    └── tests

These files are used in the development of decanter itself, and should be removed:

::

    mv decanter/decanter tmp && rm -rf decanter && mv tmp decanter

You should end up with a directory structure like this. Congratulations!

::

    decanter
    ├── __init__.py
    ├── app
    ├── config
    ├── decanter.py
    ├── lib
    └── vendor
