from distutils.core import Command
import os
import sys
from setuptools import setup, find_packages
from subprocess import call

# Command based on Libcloud setup.py:
# https://github.com/apache/libcloud/blob/trunk/setup.py


class Pep8Command(Command):
    description = "Run pep8 script"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            import pep8
            pep8
        except ImportError:
            print ('Missing "pep8" library. You can install it using pip: '
                   'pip install pep8')
            sys.exit(1)

        cwd = os.getcwd()
        retcode = call(('pep8 %s/decanter/' % (cwd)).split(' '))
        sys.exit(retcode)

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
    cmdclass={
        'pep8': Pep8Command,
    },
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
