# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from aldryn_events import __version__

REQUIREMENTS = [
    'Django<1.8,>=1.3',
    'South<1.1,>=1.0.2',
    'django-extended-choices',
    'django-tablib',
    'django-appconf',
    'django-standard-form',
    'djangocms-text-ckeditor',
    'aldryn-common>=0.0.6',
    'django-filer',
    'django-hvad',
    'django-sortedm2m',
    'django-parler',
    'aldryn-apphooks-config',
    'django-reversion'
]

DEPENDENCY_LINKS = [
    'git+https://github.com/aldryn/aldryn-apphooks-config@v0.1.2#egg=aldryn-apphooks-config-0.1.2'
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
