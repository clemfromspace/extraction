from distutils.core import setup

setup(
    name='extraction',
    version='0.1.0',
    author='Will Larson',
    author_email='lethain@gmail.com',
    packages=['extraction'],
    scripts=['bin/extraction.py'],
    url='http://pypi.python.org/pypi/extraction//',
    license='LICENSE.txt',
    description='Extract basic info from HTML webpages.',
    long_description=open('README.txt').read(),
)