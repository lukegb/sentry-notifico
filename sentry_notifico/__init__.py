"""
sentry_notifico
===============

:copyright: (c) 2013 by Luke Granger-Brown, see AUTHORS for more details.
:license: MIT License, see LICENSE for more details.
"""

try:
	VERSION = __import__('pkg_resources') \
		.get_distribution('sentry-notifico').version
except Exception, e:
	VERSION = 'unknown'