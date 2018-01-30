# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_events import __version__

REQUIREMENTS = [
    'aldryn-apphooks-config>=0.1.4',
    'aldryn-boilerplates',
    'aldryn-common>=0.0.6',
    'aldryn-translation-tools>=0.2.1',
    'django-appconf',
    'django-appdata<0.2',
    'django-bootstrap3',
    'django-cms>=3.2',
    'django-extended-choices',
    'django-filer',
    'django-parler>=1.6.1',
    'django-sortedm2m>=1.2.2',
    'django-standard-form>=1.1.1',
    'django-tablib',
    'djangocms-text-ckeditor',
    'python-dateutil',
    'six',
    'Django>=1.8,<2',
]

# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 1.8',
    'Framework :: Django :: 1.9',
    'Framework :: Django :: 1.10',
    'Framework :: Django :: 1.11',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
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
