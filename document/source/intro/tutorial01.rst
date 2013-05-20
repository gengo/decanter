.. index::
   single: HelloWorld

===========
Hello World
===========

Start decanter
==============

Execute this command.

::

    ./decanter.py -c config/devel.py start

If successful, it should output this message:

::

    Starting daemon with pidfile: {path/to/workspace}/gen/run/decanter_9000.py

Access in browser
=================

Try to access http://localhost:9000/ in your favorite browser.
Did you see this message?

::

    {
        word: "Hello Decanter!"
    }

Stop decanter
=============

To stop decanter, run this command:

::

    ./decanter.py -c config/devel.py stop

Because the decanter stopped, can not access in browser.

And of course, to start decanter again, you can run this command again:

::

    ./decanter.py -c config/devel.py start
