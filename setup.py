# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from aldryn_events import __version__

py26 = sys.version_info < (2, 7, 0) and sys.version_info >= (2, 6, 0)
py27 = sys.version_info < (2, 8, 0) and sys.version_info >= (2, 7, 0)

if not py27:
    raise ValueError(
        "Aldryn Events currently support only python 2.7 at this time, "
        "not {0}".format(sys.version_info)
    )

REQUIREMENTS = [
    'Django>=1.6,<1.8',
    'aldryn-apphooks-config>=0.1.4',
    'aldryn-boilerplates',
    'aldryn-common>=0.0.6',
    'aldryn-translation-tools>=0.0.7',
    'aldryn-reversion>=0.0.2,<0.1.0',
    'django-appconf',
    'django-bootstrap3',
    'django-extended-choices',
    'django-filer',
    'django-parler',
    'django-sortedm2m',
    'django-standard-form>=1.1.1',
    'django-tablib>=3.0',
    'djangocms-text-ckeditor',
    'python-dateutil',
]

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.6',
    'Framework :: Django :: 1.7',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]


setup(
    name='aldryn-events',
    version=__version__,
    description='An events app for Aldryn',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-events',
    packages=find_packages(),
    license='LICENSE.txt',
    platforms=['OS Independent'],
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    long_description=open('README.rst').read(),
    include_package_data=True,
    zip_safe=False,
)
