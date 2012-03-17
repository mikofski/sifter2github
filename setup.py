try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'A simple tool for migrating issues from Sifter to Github',
	'author': 'Jeff Roche',
	'url': '',
	'download_url': '',
	'author_email': 'jeff.roche@gmail.com',
	'version': '0.1',
	'install_requires': ['py-github'],
	'packages': ['sifter2github'],
	'scripts': [],
	'name': 'sifter2github'
}

setup(**config)