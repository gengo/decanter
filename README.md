[![Build Status](https://travis-ci.org/gengo/decanter.png?branch=master)](https://travis-ci.org/gengo/decanter)
decanter
========

A web framework based on [bottle](http://bottlepy.org/docs/stable/), see [requirements.txt](https://github.com/gengo/decanter/blob/master/install/requirements.txt) for a list of requirements. On Ubuntu, you will also need to have these extra packages installed: `sudo apt-get install python-dev libevent-dev`


### To run it
./decanter.py -h hostname -p port -c config.module start|stop|restart|status|runserver

**config.module** must match the location of a module containing decanter required configuration items, i.e. config/devel.py but without the .py extension.


### Overview
Decanter does not particularly favor convention over configuration, it uses a combination of both, and it adds structure to bottle framework.

For example the app directory path is set in the configuration file, while the structure of the directory uses the following convention:

* app
    - bundles
        - home
            - controllers
            - views
        - admin
            - controllers
            - views
    - config
        - environment
            - devel.py
            - live.py
        - settings.py
    - views

#### Bundles, controllers and the url path
In the controllers directory there are modules with bottle style routes. Default bundle and default controller are configured in the configuration module (i.e. config.devel.py), so the single forward slash path "/" will load the default controller in the default bundle.
While a path such as "/admin/home/" will load the controller home.py inside the controllers directory in the admin bundle.

#### Decanter routes
Decanter routes override [bottle routes](http://bottlepy.org/docs/stable/tutorial.html#request-routing), (see lib/decorator.py) and they fix a couple of things:

1. "apply" route parameter takes the string name of the plugin i.e. "jinja2" or "json" or a list of strings rather then an object or list of objects like in bottle
2. the following two paths are the same "/home/" and "/home" in both the browser and decanter route.

#### Bundles, controllers and views
Decanter overrides bottle jinja2 plugin. Templates are expected to by found in the "views" directory of each bundle, and if not found there the "bundle/views" directory is searched.

Templates name should, by convention, follow the bundle/controller/action name, i.e. if the "index" action in the "home" controller within the "admin" bundle is executed then by default a jinja2 template with the following name: "admin/home/index.html" will be loaded from the admin/views bundle directory if present, otherwise the "bundles/views" directory will be searched, if the template is not found the process is repeated searching for home/index.html in the "admin/views/" directory first the again the "bundles/views/".






