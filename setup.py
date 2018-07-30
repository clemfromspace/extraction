from setuptools import setup

setup(
    name='extraction',
    version='0.2',
    author='Will Larson',
    author_email='lethain@gmail.com',
    packages=['extraction', 'extraction.tests', 'extraction.examples'],
    url='http://pypi.python.org/pypi/extraction/',
    license='LICENSE.txt',
    description='Extract basic info from HTML webpages.',
    install_requires=[
        "parsel==1.5.0"
    ],
)
