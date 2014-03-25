'''
    Craftsy Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from lib.plugin import CraftsyPlugin

plugin = CraftsyPlugin()
mode = plugin.addon.queries['mode']
play = plugin.addon.queries.get('play', None)

if play:
    print "We are playing"
    url = plugin.resolve_url(plugin.addon.queries.get('url'))
    if (url == None):
        plugin.addon.show_error_dialog(['There is a problem fetching', 'the movie URL']);
    else:
        plugin.addon.resolve_url(url)

elif mode == 'resolver_settings':
    urlresolver.display_settings()

elif mode == 'classes':
    url = plugin.addon.queries.get('url')
    plugin.add_lessons(url)

elif mode == 'main':
    if (plugin.do_login()):
        plugin.add_classes()
    else:
        plugin.addon.show_error_dialog(['There is a problem loggin in. ', 'Check your settings and if those are ', 'correct, then check the logs'])

if not play:
    plugin.addon.end_of_directory()


