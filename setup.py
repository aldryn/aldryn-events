# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_events import __version__

REQUIREMENTS = [
    'Django>=1.3,<1.6',
    'djangocms-common',
    'django-extended-choices',
    'django-tablib',
    'django-appconf',
    'django-standard-form',
    'djangocms-text-ckeditor',
    'aldryn-search>=0.1.9',
    'aldryn-common>=0.0.3',
    'django-filer',
    'django-hvad',
    'django-sortedm2m',
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
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
    include_package_data=True,
    zip_safe=False
)
