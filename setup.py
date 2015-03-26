# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages
from aldryn_events import __version__

py26 = sys.version_info < (2, 7, 0) and sys.version_info >= (2, 6, 0)
py27 = sys.version_info < (2, 8, 0) and sys.version_info >= (2, 7, 0)

if not py26 and not py27:
    raise ValueError(
        "Aldryn Events currently support only python 2.6 to 2.7, "
        "not {0}".format(sys.version_info)
    )

REQUIREMENTS = [
    'aldryn-apphooks-config>=0.1.4',
    'aldryn-boilerplates',
    'aldryn-common>=0.0.6',
    'django-appconf',
    'django-bootstrap3',
    'django-extended-choices',
    'django-filer',
    'django-parler',
    'django-sortedm2m',
    'django-standard-form>=1.1.1',
    'django-tablib',
    'djangocms-text-ckeditor',
    'python-dateutil',
]


DEPENDENCY_LINKS = [
    'https://github.com/aldryn/aldryn-apphooks-config/archive/master.zip#egg=aldryn-apphooks-config'  # NOQA
]

if py26:
    REQUIREMENTS += [
        'Django<1.7,>=1.6',
        'South<1.1,>=1.0.2'
    ]
    DEPENDENCY_LINKS += [
        'https://github.com/anrie/django-tablib/archive/master.zip#egg=django-tablib-3.0.2.1'  # NOQA
    ]

if py27:
    REQUIREMENTS += [
        'Django<1.8,>=1.6',
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
    dependency_links=DEPENDENCY_LINKS,
    classifiers=CLASSIFIERS,
    include_package_data=True,
    zip_safe=False
)
