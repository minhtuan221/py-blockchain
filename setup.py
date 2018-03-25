#!/usr/bin/env python
import easy_blockchain
from setuptools import setup, find_packages

# python setup.py register -r pypi
# python setup.py sdist bdist_wheel
# twine upload dist/*

# I really prefer Markdown to reStructuredText.  PyPi does not.  This allows me
# to have things how I'd like, but not throw complaints when people are trying
# to install the package and they don't have pypandoc or the README in the
# right place.
readme = ''
try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   readme = ''


setup(
    name='easy_blockchain',
    version='0.1.6',
    description='A blockchain for human',
    long_description=readme,
    author='Minh Tuan Nguyen',
    author_email='ntuan221@gmail.com',
    license='BSD',
    platforms='any',
    url='https://github.com/minhtuan221/py-blockchain',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6', 
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    keywords=['microservice', 'http', 'flask','ecdsa','blockchain'],
    # entry_points={'console_scripts': [
    #     'microservices_connector = microservices_connector:main',
    # ]},
    packages=find_packages(exclude=('test*', 'testpandoc*','image*')),
    include_package_data=False,
    install_requires=['flask','requests','ecdsa'],
)
