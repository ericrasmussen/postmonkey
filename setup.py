__version__ = '1.0a4'

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='postmonkey',
      version=__version__,
      description='Python wrapper for Mailchimp API',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        'Intended Audience :: Developers',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ],
      keywords='mailchimp',
      author='Eric Rasmussen',
      author_email='eric@chromaticleaves.com',
      url='http://python.chromaticleaves.com/docs/postmonkey/',
      license='FreeBSD',
      packages=['postmonkey'],
      test_suite='postmonkey.tests',
      include_package_data=True,
      zip_safe=False,
      tests_require=['pkginfo', 'nose'],
      install_requires=['requests'],
)
