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

It is success if this message is output.

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

Do you hate that hold running a decanter? Execute this command.

::

    ./decanter.py -c config/devel.py stop

Because the decanter stopped, can not access in browser.

Of course, the decanter starts when you execute this command again.

::

    ./decanter.py -c config/devel.py start
