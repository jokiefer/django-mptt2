import os
import re
from distutils.command.build import build

from setuptools import setup


class pre_build(build):
    
    def run(self):
        from django.core.management.commands.compilemessages import \
            compile_messages
        compile_messages()

        self.run_command("npm install")
        build.run(self)


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]",
                     init_py, re.MULTILINE).group(1)


version = get_version("mptt2")

setup(
    cmdclass={
        'pre_build': pre_build
    },
    version=version,
)
