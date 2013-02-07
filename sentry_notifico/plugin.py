"""
sentry_notifico.plugin
======================

:copyright: (c) 2013 by Luke Granger-Brown, see AUTHORS for more details.
:license: MIT License, see LICENSE for more details.

This is a placeholder file, because Django requires it for inclusion in INSTALLED_APPS.
It serves no other purpose.
"""

import urllib2
from urllib import urlencode

from django import forms
from django.utils.translation import ugettext_lazy as _

from sentry.conf import settings
from sentry.utils.safe import safe_execute
from sentry.plugins import Plugin

import sentry_notifico

class NotificoOptionsForm(forms.Form):
	message_hook_url = forms.CharField(label=_('"Plain Text" Message Hook URL'),
		help_text=_('Enter Notifico plain text hook endpoint (e.g. from http://n.tkte.ch)'),
		widget=forms.TextInput(attrs={
			'class': 'span12',
			'placeholder': 'http://n.tkte.ch/h/something/here'
			})
		)
	format = forms.CharField(label=_('Message format'),
		help_text=_('Use the %(field_name)s format to substitute information - ' + \
			'available fields are: id, checksum, project_slug, project_name, logger,' + \
			' level, culprit, message, failed_url, error_line, event_url.'),
		widget=forms.TextInput(attrs={
			'class': 'span12'
			})
		)
	new_only = forms.BooleanField(help_text=_('Only send messages for new events.'), required=False)

class NotificoPlugin(Plugin):
	author = 'Luke Granger-Brown'
	author_url = 'https://github.com/lukegb/sentry-notifico'
	version = sentry_notifico.VERSION
	description = 'Integrates Notifico support.'
	resource_links = [
		('Public Notifico Instance', 'http://n.tkte.ch'),
		('Bug Tracker', 'https://github.com/lukegb/sentry-notifico/issues'),
		('Source', 'https://github.com/lukegb/sentry-notifico')
	]

	slug = 'notifico'
	title = _('Notifico')
	conf_title = _('Notifico')
	conf_key = 'notifico'
	project_conf_form = NotificoOptionsForm

	def is_configured(self, project, **kwargs):
		return all((self.get_option(k, project) for k in ('message_hook_url', 'format')))

	def send_to_notifico(self, url, message):
		# Notifico takes a single argument, via POST or GET (we're using POST)
		# so build the object
		data = {
			'payload': message
		}
		# now the request
		req = urllib2.Request(url, urlencode(data))
		# send the request, get a response
		resp = urllib2.urlopen(req)
		# return the response, if anyone cares
		return resp

	def post_process(self, group, event, is_new, is_sample, **kwargs):
		# should we send this?
		only_new = self.get_option('new_only', event.project)
		if only_new and not is_new:
			# no, we shouldn't
			return

		if not self.is_configured(group.project):
			# bail!
			return

		# get the configuration variables
		endpoint = self.get_option('message_hook_url', event.project)
		format = self.get_option('format', event.project)

		if endpoint and format:
			# we need to build the URL
			# this is might throw a KeyError(?!)
			try:
				failed_url = event.request.build_absolute_uri()
			except Exception, e:
				failed_url = ''

			if failed_url == '':
				# oh, the irony.
				failed_url = '(URL unavailable)'

			# helper for building this up:
			event_url = '/%s/%s/group/%d/events/%d/' % (group.project.team.slug, group.project.slug, group.id, event.id)

			# we need:
			# id, checksum, project_slug, project_name, 
			# logger, level, culprit, message, failed_url
			data = {
				'id': str(group.id),
				'checksum': group.checksum,
				'project_slug': group.project.slug,
				'project_name': group.project.name,
				'logger': group.logger,
				'level': group.get_level_display(),
				'culprit': group.culprit,
				'message': event.message,
				'failed_url': failed_url,
				'error_line': event.error().encode('utf-8').split('\n')[0],
				'event_url': event_url
			}

			# now we have the data and the format string
			# glue them together
			formatted_data = format % data

			# so send it:
			safe_execute(self.send_to_notifico, endpoint, formatted_data)