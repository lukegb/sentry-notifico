#!/usr/bin/env python
"""
sentry-notifico
===============

An extension for Sentry which makes calls to Notifico or
Notifico-like API, which will ping IRC using its own bot.

:copyright: (c) 2013 by Luke Granger-Brown, see AUTHORS for more details.
:license: MIT License, see LICENSE for more details.
"""
from setuptools import setup

tests_require = [
	'nose==1.1.2',
]

install_requires = [
	'sentry>=4.6.0',
]

setup(
	name='sentry-notifico',
	version='1.0',
	description='Notifico plugin for Sentry',
	author='Luke Granger-Brown',
	author_email='git@lukegb.com',
	url='https://github.com/lukegb/sentry-notifico/',
	packages=['sentry_notifico'],
	entry_points={
		'sentry.plugins': [
			'notifico = sentry_notifico.plugin:NotificoPlugin',
		],
	},
)