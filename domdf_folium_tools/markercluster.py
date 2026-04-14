#!/usr/bin/env python3
#
#  markercluster.py
"""
Customisations to the marker cluster plugin.
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
from collections.abc import Sequence
from typing import Any, Optional, Union

# 3rd party
from folium import CustomIcon, DivIcon, Icon, Popup, Tooltip
from folium.map import Layer, Marker
from folium.plugins import MarkerCluster as FoliumMarkerCluster
from folium.template import Template
from folium.utilities import TypeJsonValue, remove_empty, validate_location

# this package
from domdf_folium_tools import __version__

__all__ = ["MarkerCluster", "MarkerGroup", "PolyMarker"]


class MarkerCluster(FoliumMarkerCluster):
	r"""
	Customised MarkerCluster plugin with support for ``chunkProgress`` and ``maxClusterRadius`` functions.

	:param \*args: Positional arguments for the oricinal ``MarkerCluster`` class.
	:param chunk_progress_function: Name of the javascript function for the ``chunkProgress`` option.
	:param max_cluster_radius_function: Name of the javascript function for the ``maxClusterRadius`` option.
	:param \*\*kwargs: Keyword arguments for the original ``MarkerCluster`` class.
	"""

	_js_constructor = "new L.MarkerClusterGroup"

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = {{ this._js_constructor }}(
                {{ this.options|tojavascript }}
            );
            {%- if this.icon_create_function is not none %}
            {{ this.get_name() }}.options.iconCreateFunction =
                {{ this.icon_create_function.strip() }};
            {%- endif %}
			{%- if this.chunk_progress_function is not none %}
            {{ this.get_name() }}.options.chunkProgress =
                {{ this.chunk_progress_function.strip() }};
            {%- endif %}
			{%- if this.max_cluster_radius_function is not none %}
            {{ this.get_name() }}.options.maxClusterRadius =
                {{ this.max_cluster_radius_function.strip() }};
            {%- endif %}
        {% endmacro %}
        """,
			)

	def __init__(
			self,
			*args: Any,
			chunk_progress_function: Optional[str] = None,
			max_cluster_radius_function: Optional[str] = None,
			**kwargs: Any,
			):
		super().__init__(*args, **kwargs)

		self.chunk_progress_function = chunk_progress_function
		self.max_cluster_radius_function = max_cluster_radius_function


class MarkerGroup(Layer):  # noqa: PRM002
	r"""
	A fake grouping of markers in a marker cluster.

	Allows markers to be shown/hidden with the layer control but maintaining a single ``MarkerClusterGroup`` underneath.

	:param cluster The Leaflet MarkerClusterGroup to add markers too.
	:param \*args: Positional arguments for the ``Layer`` class.
	:param \*\*kwargs: Keyword arguments for the ``Layer`` class.

	"""

	_js_constructor = "new L.MarkerGroup"

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = {{ this._js_constructor }}(
				{{ this.cluster.get_name() }},
                {{ this.options|tojavascript }}
            );

        {% endmacro %}
        """,
			)

	default_js = [
			(
					"domdf_folium_tools_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/domdf-folium-tools.min.js",
					),
			]

	def __init__(
			self,
			cluster: FoliumMarkerCluster,
			name: Optional[str] = None,
			overlay: bool = True,
			control: bool = True,
			show: bool = True,
			**kwargs: TypeJsonValue,
			):
		super().__init__(name=name, overlay=overlay, control=control, show=show)
		self.cluster = cluster
		self._name = "MarkerGroup"
		self.options = remove_empty(**kwargs)


class PolyMarker(Marker):  # noqa: PRM002
	r"""
	A Leaflet Marker which also adds a polygon (or polygons).

	If the marker is removed (manually or via a markercluster) the polygon is removed too.

	:param latlng: The coordinates of the marker.
 	:param poly_points: List of lists giving coordinates of the polygon(s) points.
 	:param \*args: Positional arguments for the original ``Marker`` class.
 	:param \*\*kwargs: Keyword arguments for the original ``Marker`` class.
	"""

	_js_constructor = "new L.PolyMarker"

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = {{ _js_constructor }}(
                {{ this.location|tojson }},
                {{ this.poly_points|tojson }},
                {{ this.options|tojavascript }}
            ).addTo({{ this._parent.get_name() }});
        {% endmacro %}
        """,
			)

	default_js = [
			(
					"domdf_folium_tools_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/domdf-folium-tools.min.js",
					),
			]

	def __init__(
			self,
			location: Optional[Sequence[float]] = None,
			poly_points: Optional[Sequence[Sequence[Sequence[float]]]
									] = None,  # List of <list of (float, float) representing a single polygon>
			popup: Union[Popup, str, None] = None,
			tooltip: Union[Tooltip, str, None] = None,
			icon: Optional[Union[Icon, CustomIcon, DivIcon]] = None,
			draggable: bool = False,
			**kwargs: TypeJsonValue,
			):
		super().__init__(
				location=location,
				popup=popup,
				tooltip=tooltip,
				icon=icon,
				draggable=draggable,
				**kwargs,
				)
		self._name = "PolyMarker"

		if poly_points is None:
			self.poly_points = None
		else:
			validated_poly_points = []

			for polygon in poly_points:
				validated_polygon = []

				for latlng in polygon:
					validated_polygon.append(validate_location(latlng))

				validated_poly_points.append(validated_polygon)

			self.poly_points = validated_poly_points
