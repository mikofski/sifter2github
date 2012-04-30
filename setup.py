try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'name': 'sifter2github',
	'version': '0.1',
	'description': 'A simple tool for migrating issues from Sifter to Github',
	'author': 'Jeff Roche',
	'url': '',
	'download_url': '',
	'author_email': 'jeff.roche@gmail.com',
	'version': '0.1',
	'install_requires': [
		'sifter-python',
		'requests>=0.11.2'
	],
	'packages': ['sifter2github'],
	'scripts': [],
}

setup(**config)