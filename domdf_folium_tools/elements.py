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
from typing import TypeVar

# 3rd party
import folium
from folium.template import Template

__all__ = ["NLSTileLayer", "Sidebar", "add_to", "set_id"]

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
