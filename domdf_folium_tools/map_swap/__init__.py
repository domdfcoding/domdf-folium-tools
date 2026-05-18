#!/usr/bin/env python3
#
#  __init__.py
"""
Folium plugin that adds a control for swapping between maps.
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

# 3rd party
import folium.elements
from folium.template import Template
from folium.utilities import remove_empty

# this package
from domdf_folium_tools import __version__

__all__ = ["MapSwapControl"]


class MapSwapControl(folium.elements.JSCSSMixin, folium.elements.MacroElement):
	r"""
	Control for swapping between maps.

	:param maps: Mapping of map names (raw HTML allowed) to hyperlinks.
	:param icon: The control's icon.
	:param \*\*kwargs: Additional options for the javascript ``MapSwapControl`` class.
	"""

	def __init__(self, maps: dict[str, str], icon: str = "fa-solid fa-map", **kwargs):
		super().__init__()
		self._name = "MapSwapControl"
		self.options = remove_empty(maps=maps, icon=icon, **kwargs)

	default_js = [
			(
					"map_swap_control_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/map_swap/map_swap_control.min.js",
					),
			]

	default_css = [
			(
					"fontawesome_css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css",
					),
			(
					"map_swap_control_css",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/map_swap/map_swap_control.min.css",
					),
			]

	_template = Template(
			"""
			{% macro header(this, kwargs) %}
				<style>
					.leaflet-control-map-swap {
						a {
							font-size: 1.4em;
							.leaflet-map-swap-icon {
								color: black;
							}
						}
					}
				</style>
			{% endmacro %}

			{% macro script(this, kwargs) %}
				var {{this.get_name()}} = new MapSwapControl(
					{{this.options | tojson}}
				)

				// Close the control when map clicked.
				{{ this._parent.get_name() }}.on('click', {{this.get_name()}}.close, {{this.get_name()}});

				{{this.get_name()}}.addTo({{ this._parent.get_name() }});
			{% endmacro %}
			""",
			)
