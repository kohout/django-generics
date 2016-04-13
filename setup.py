import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-generics',
    version='0.2',
    packages=['generics'],
    include_package_data=True,
    license='Unlicense',  # example license
    description='A repository containing a lot of helpful classes and shortcuts for developing with class-based (generic) views',
    long_description=README,
    url='https://github.com/kohout/django-generics/',
    author='Christian Kohout',
    author_email='ck@getaweb.at',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
