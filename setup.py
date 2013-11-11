from setuptools import setup, find_packages

setup(
    name = "aldryn-events",
    version = __import__('aldryn_events').__version__,
    url = 'http://github.com/aldryn/aldryn-events',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "A simple events App for django CMS Cloud.",
    author = 'Divio AG',
    author_email = 'developers@divio.ch',
    packages=find_packages(),
    install_requires = (
        'Django>=1.3,<1.6',
        'djangocms-common',
        'django-extended-choices',
        'django-tablib',
        'django-appconf',
        'django-standard-form',
        'djangocms-text-ckeditor',
        'aldryn-search>=0.1.3',
    ),
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
