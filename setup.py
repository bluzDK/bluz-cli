from setuptools import find_packages
from distutils.core import setup

from bluz_cli import __version__


setup(name              = 'bluz_cli',
      version           = __version__,
      author            = 'Eric Ely',
      author_email      = 'ericely@bluz.io',
      description       = 'CLI for bluz',
      license           = 'Other/Proprietary License',
      url               = 'https://github.com/bluzDK/bluz-cli',
      install_requires  = ['pyserial', 'requests'],
      entry_points      = {'console_scripts': ['bluz = bluz_cli.__main__:main']},
      packages          = find_packages(),
      include_package_data=True,
      py_modules=['bluz_cli'],
      package_data={
            'bluz_cli': ['resources/*', 'resources/keys/*', 'resources/production_firmware/*', 'resources/provisioning_firmware/*', 'resources/s110/*']
      }
)