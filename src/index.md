---
layout: default
title: Structure for Python Bottle web projects
---
Decanter is a python-based micro web framework that adds structure to vanilla Bottle apps. It  standardizes folder structure for apps that inevitably grow bigger, and allows web developers to start such projects in a matter of seconds.

### Getting Started

To download decanter and start your first project, simply run the following in a terminal:

{% highlight bash %}
pip install decanter
decanter create myproject
{% endhighlight %}

The `decanter create [projectname]` command creates a base directory structure with an example view and controller. To test that it's working, you can now run the server:

{% highlight bash %}
cd hello
python manage.py runserver
{% endhighlight %}

This will start the decanter server on port 9000. Point your browser to `http://localhost:9000`, and you should be seeing a `Hello 世界` message!

### Directory Structure

The app directory path is set in the configuration file, while the directory structure uses the following convention:

* app
    - bundles
        - home
            - controllers
            - views
        - admin
            - controllers
            - views
    - views

This skeleton structure is automatically created when you call the `decanter create [projectname]` command.

### Other things

##### Bundles, controllers and the url path
In the controllers directory there are modules with bottle style routes. Default bundle and default controller are configured in the configuration module (i.e. config.devel.py), so the single forward slash path "/" will load the default controller in the default bundle.
While a path such as "/admin/home/" will load the controller home.py inside the controllers directory in the admin bundle.

##### Decanter routes

Decanter routes override [bottle routes](http://bottlepy.org/docs/stable/tutorial.html#request-routing), (see lib/decorator.py) and they fix a couple of things:

1. "apply" route parameter takes the string name of the plugin i.e. "jinja2" or "json" or a list of strings rather then an object or list of objects like in bottle
2. the following two paths are the same "/home/" and "/home" in both the browser and decanter route.

### Recommendations

 - Bring your own ORM
 - Put repeated functionality in bundles and distribute via `pip`

### Get Involved

Decanter is open-source and BSD-licensed. Check out [the code on Github](https://github.com/gengo/decanter), open issues and put in pull requests. We welcome any contributions!

---------------------------------------

Decanter is a minimalistic python-based web framework developed by the friendly folks at [Gengo](http://gengo.com), based in Tokyo. It's a tool used internally and currently still in an alpha pre-release stage, so feel free to drop us a line and tell us what you think!
