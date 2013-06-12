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
        retcode = call(("pep8 %s/decanter/ --exclude=vendor --ignore=E501" % (cwd)).split(' '))
        sys.exit(retcode)

class TestCommand(Command):
    description = "Run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call(['nosetests', '--debug=DEBUG', '-s'])
        raise SystemExit(errno)

# Required repositories
with open(os.path.join(os.path.dirname(__file__),'requirements.txt')) as f:
    install_requires = f.read().splitlines()

setup(
    name="decanter",
    version="0.1.4",
    packages=find_packages(),
    scripts=['decanter/decanter.py'],
    install_requires=install_requires,

    package_data={
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
        'test': TestCommand,
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
