from setuptools import setup, find_packages
import os
setup(
    name = "decanter",
    version = "0.1.0",
    packages = find_packages(),
    scripts = ['decanter/decanter.py'],

    # Required repositories 
    install_requires = [
        'Jinja2==2.6',
        'MarkupSafe==0.15',
        'argparse==1.2.1',
        'bottle==0.11.6',
        'gevent==0.13.8',
        'greenlet==0.4.0',
        'requests==1.2.0',
        'wsgiref==0.1.2',
    ],

    package_data = {
        # If any package contains *.txt, *.rst or *.md files, include them:
        '': ['*.txt', '*.rst', '*.md'],
    },

    # metadata for upload to PyPI
    author = "Andrea Belvedere",
    author_email = "andrea.belvedere@gengo.com",
    description = "A humble web framework based on bottle",
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    license = "BSD",
    keywords = "web framework bottle gengo",
    url = "https://github.com/gengo/decanter",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet'
    ]

)