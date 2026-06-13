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
from collections.abc import Sequence
from typing import NamedTuple, Optional, TypeVar, Union

# 3rd party
import branca.element
import folium
from folium.elements import JSCSSMixin
from folium.plugins import LocateControl as FoliumLocateControl
from folium.template import Template
from folium.utilities import TypeJsonValue, parse_options, remove_empty
from folium.vector_layers import path_options

__all__ = [
		"add_to",
		"Arrow",
		"Components",
		"ExtraMarkersIcon",
		"LocateControl",
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


class ExtraMarkersIcon(JSCSSMixin, folium.Icon):
	r"""
	Modified Folium icon that uses Leaflet.ExtraMarkers.

	:param color: The color of the marker. Some colours may require ``svg=True``.
	:param icon_color: The color of the drawing on the marker.
	:param icon: The name of Font Awesome icon for the marker.
	:param angle: The icon will be rotated by this amount of degrees.
	:param prefix: The prefix states the source of the icon. 'fa' for font-awesome or 'glyphicon' for bootstrap 3.
	:param \*\*kwargs: Other options for the icon.

	https://github.com/coryasilva/Leaflet.ExtraMarkers
	"""

	default_js = [
			(
					"extra_markers_js",
					"https://unpkg.com/leaflet-extra-markers@1.2.2/dist/js/leaflet.extra-markers.js",
					),
			]

	default_css = [
			(
					"extra_markers_css",
					"https://unpkg.com/leaflet-extra-markers@1.2.2/dist/css/leaflet.extra-markers.min.css",
					),
			]

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{ this.get_name() }} = new L.ExtraMarkers.Icon(
				{{ this.options|tojavascript }}
			);
		{% endmacro %}
		""",
			)

	def __init__(
			self,
			color: str = "blue",
			icon_color: str = "white",
			icon: str = "fa-circle-info",
			angle: int = 0,
			prefix: str = "fa",
			**kwargs: TypeJsonValue,
			):
		super().__init__()
		self._name = "Icon"
		self.options = remove_empty(
				marker_color=color,
				icon_color=icon_color,
				icon=icon,
				prefix=prefix,
				extra_classes=f"fa-rotate-{angle}",
				**kwargs,
				)


class Arrow(JSCSSMixin, folium.PolyLine):
	r"""
	Modified Folium PolyLine with an arrowhead at the end.

	See :func:`folium.vector_layers.path_options` for the `Path` options.

	:param locations: List of points ``(latitude, longitude)`` for the line.
		Pass multiple sequences of coordinates for a multi-polyline.
	:param popup: Input text or visualization for object displayed when clicking.
	:param tooltip: Display a text when hovering over the object.
	:param arrowhead_options: Options for the arrowhead.
		See https://github.com/slutske22/leaflet-arrowheads#options
	:param \*\*kwargs: Other valid (possibly inherited) options.
		See https://leafletjs.com/reference.html#polyline
	"""

	default_js = [
			(
					"leaflet_geometryutil_js",
					"https://cdn.jsdelivr.net/npm/leaflet-geometryutil@0.10.3/src/leaflet.geometryutil.min.js",
					),
			(
					"leaflet_arrowheads_js",
					"https://cdn.jsdelivr.net/npm/leaflet-arrowheads@1.4.0/src/leaflet-arrowheads.min.js",
					),
			]

	def __init__(
			self,
			locations: Union[Sequence[tuple[float, float]], Sequence[Sequence[tuple[float, float]]]],
			popup: Union[str, folium.Popup, None] = None,
			tooltip: Union[str, folium.Tooltip, None] = None,
			arrowhead_options: Optional[dict[str, TypeJsonValue]] = None,
			**kwargs: TypeJsonValue,
			):
		super().__init__(locations, popup=popup, tooltip=tooltip)
		self._name = "PolyLine"

		# mypy is unhappy but it's like this in Folium itself
		self.options = path_options(line=True, **kwargs)  # type: ignore[arg-type]

		self.arrowhead_options = parse_options(**(arrowhead_options or {}))

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{ this.get_name() }} = L.polyline(
				{{ this.locations|tojson }},
				{{ this.options|tojson }}
			).addTo({{this._parent.get_name()}});
			{{ this.get_name() }}.arrowheads({{ this.arrowhead_options|tojson }});
		{% endmacro %}
		""",
			)


class LocateControl(FoliumLocateControl):
	"""
	Modified Folium LocateControl to geolocate the user.

	Sets default options and updates the plugin version.
	"""

	default_css = [
			(
					"Control_locate_min_css",
					"https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.90.0/dist/L.Control.Locate.min.css",
					),
			(
					"fontawesome_css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css",
					),
			]
	default_js = [
			(
					"Control_locate_min_js",
					"https://cdn.jsdelivr.net/npm/leaflet.locatecontrol@0.90.0/dist/L.Control.Locate.min.js",
					),
			]

	_template = Template(
			"""
			{% macro header(this, kwargs) %}
				<style>
					.leaflet-control-locate {
						a {
							font-size: 1.4em;
							.leaflet-locate-icon {
								color: black
							}
						}
					}
				</style>
			{% endmacro %}

			{% macro script(this, kwargs) %}
				var {{this.get_name()}} = L.control.locate(
					{{this.options | tojson}}
				).addTo({{ this._parent.get_name() }});
				{% if this.auto_start %}
					{{this.get_name()}}.start();
				{% endif %}
			{% endmacro %}
			""",
			)

	def __init__(self):
		super().__init__(
				icon="fa-solid fa-location-crosshairs",
				keepCurrentZoomLevel=[13, 18],
				locateOptions={"enableHighAccuracy": True, "maxZoom": 16},
				)

	def get_name(self) -> str:  # noqa: D102
		return "locate_control"
