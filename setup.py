from distutils.core import Command
import os
import sys
from setuptools import setup, find_packages
from subprocess import call


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
            print('Missing "pep8" library. You can install it using pip: '
                  'pip install pep8')
            sys.exit(1)

        cwd = os.getcwd()
        retcode = call(("pep8 %s/decanter/ --exclude=vendor --ignore=E501" % (
            cwd)).split(' '))
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
        errno = subprocess.call(['nosetests', '--debug=DEBUG', '-s', 'tests/unit'])
        raise SystemExit(errno)


class TestCommandWithCoverage(Command):
    description = "Run tests and generate coverage report"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call(['nosetests', '--with-cover', '--cover-html', '--cover-package=decanter', 'tests/unit'])
        raise SystemExit(errno)


# Required repositories
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    install_requires = f.read().splitlines()

setup(
    name="decanter",
    version=open('decanter/_version.py').readlines()[-1].split()[-1].strip("\"'"),
    packages=find_packages(),
    scripts=['decanter/decanter-admin.py'],
    install_requires=(
        "Jinja2==2.6",
        "MarkupSafe==0.15",
        "argparse==1.2.1",
        "bottle==0.11.6",
        "gevent==0.13.8",
        "greenlet==0.4.0",
        "jsonschema==1.3.0",
        "mock==1.0.1",
        "nose==1.3.0",
        "pep8==1.4.5",
        "phpserialize",
        "pika==0.9.13",
        "pycrypto==2.6",
        "redis==2.7.5",
        "requests==1.2.0",
        "unittest2==0.5.1",
        "wsgiref==0.1.2",
    ),

    package_data={
        # If any package contains *.txt, *.rst or *.md files, include them:
        '': ['*.txt', '*.rst', '*.md'],
    },

    # metadata for upload to PyPI
    author="Gengo",
    author_email="",
    description="A humble web framework based on bottle",
    long_description=open(os.path.join(
        os.path.dirname(__file__), 'README.md')).read(),
    cmdclass={
        'pep8': Pep8Command,
        'test': TestCommand,
        'coverage': TestCommandWithCoverage,
    },
    license="BSD",
    keywords="web framework bottle gengo",
    url="https://github.com/gengo/decanter",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet'
    ]

)
