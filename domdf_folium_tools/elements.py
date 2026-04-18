#!/usr/bin/env python3
#
#  elements.py
"""
Modified folium elements.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from collections import OrderedDict
from typing import NamedTuple, TypeVar

# 3rd party
import branca.element
import folium
from folium.template import Template

__all__ = [
		"add_to",
		"Components",
		"NLSTileLayer",
		"Preload",
		"render_figure",
		"set_id",
		"Sidebar",
		]

_E = TypeVar("_E", bound=folium.Element)


def set_id(element: _E, new_id: str) -> _E:
	"""
	Set the ID for the given element, for use in the generated javascript.

	:param element:
	:param new_id:
	"""

	element._id = new_id
	return element


def add_to(
		element: _E,
		parent: folium.Element,
		new_id: str,
		) -> _E:
	"""
	Add the given element to the given parent.

	:param element:
	:param parent: The parent element.
	:param new_id: ID for the given element, for use in the generated javascript.
	"""

	element = set_id(element, new_id)
	element.add_to(parent)
	return element


class NLSTileLayer(folium.TileLayer):
	r"""
	Folium TileLayer for National Library of Scotland's old Ordnance Survey Maps.

	:param name: The map name.
	:param url: The XYZ tiles URL.
	:param \*\*kwargs: Other keyword arguments for :class:`folium.TileLayer`.
		Set ``max_native_zoom`` to the value indicated on the NLS website for the particular map.
	"""

	def __init__(self, name: str, url: str, **kwargs):
		attr = f"{name} | <a href='https://maps.nls.uk'>maps.nls.uk</a> | CC-BY"
		super().__init__(
				url,
				name=name,
				min_zoom=1,
				max_zoom=20,
				attr=attr,
				**kwargs,
				)


class Sidebar(folium.MacroElement):
	"""
	JavaScript implementation for ``folium-sidebar-v2``.
	"""

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var sidebar = L.control.sidebar('sidebar').addTo({{ this._parent.get_name() }});
		{% endmacro %}
	""",
			)

	def __init__(self):
		super().__init__()
		self._name = "Sidebar"


class Components(NamedTuple):
	"""
	Figure elements produced by :func:`~.render_figure`.
	"""

	#: Header tags
	header: str
	#: Page body tags
	body: str
	#: Javascript code to insert within `<script>` tags.
	script: str
	#: Script tags to load external javascript
	scripts: str


def render_figure(figure: branca.element.Figure) -> Components:
	"""
	Render a figure for insertion into another template (flask, jinja2 etc.).

	:param figure:
	"""

	for child in figure._children.values():
		child.render()

	header_elems = OrderedDict()
	js_libs = branca.element.Element()
	js_libs._parent = figure

	for name, elem in figure.header._children.items():
		if isinstance(elem, branca.element.JavascriptLink):
			js_libs.add_child(elem, name)
		else:
			header_elems[name] = elem

	figure.header._children = header_elems

	return Components(
			header=figure.header.render(),
			body=figure.html.render(),
			script=figure.script.render(),
			scripts=js_libs.render(),
			)


class Preload(branca.element.MacroElement):
	"""
	Adds preload tags to the HTML header.

	Useful for avoiding marker image "pop-in".
	"""

	def __init__(self):
		super().__init__()
		self._name = "Preload"
		self._preloads = []

	def add_preload(self, url: str, load_as: str) -> None:
		"""
		Add a URL to be preloaded.

		:param url:
		:param load_as: The resource type, such as ``image``, ``style``, ``script``, ``font``.
		"""

		# TODO: media queries

		self._preloads.append((url, load_as))

	_template = Template(
			"""
{%- macro header(this, kwargs)%}
	{%- for (url, load_as) in this._preloads -%}
		<link rel="preload" href="{{ url }}" as="{{ load_as }}" />
	{% endfor -%}
{% endmacro -%}
		""",
			)
