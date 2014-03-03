import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='langdeath',
    version='0.1',
    packages=['dld', 'langdeath', 'ml'],
    include_package_data=True,
    description='Digital Language Death.',
    #url='http://www.example.com/',  #TODO
    author='Judit Acs',
    author_email='judit@sch.bme.hu',
    install_requires=[
        'django==1.6',
        'django-jsonfield',
    ]
)