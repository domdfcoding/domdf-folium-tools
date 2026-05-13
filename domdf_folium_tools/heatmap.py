#!/usr/bin/env python3
#
#  heatmap.py
"""
Cumulative heatmaps – data from all previous time windows is included in the "current" view.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
#  Copyright © 2013-, Folium developers
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
import json
from typing import Optional, Union, cast

# 3rd party
from folium import Control
from folium.elements import JSCSSMixin
from folium.map import Layer
from folium.template import Template
from folium.utilities import TypePosition, parse_options

# this package
from domdf_folium_tools import __version__

__all__ = ["HeatLayerWithTime", "HeatMapWithTime"]

# TODO: tojson filter that doesn't quote dict keys
# TODO: validate that TimeDimensionControl has been added when rendering


class TimeDimensionControl(Control):
	"""
	Create a ``TimeDimensionControl``.

	:param index: Index giving the label (or timestamp) of the elements of data.
	:param auto_play: Automatically play the animation across time.
	:param display_index: Display the index (usually time) in the time control.
	:param index_steps: Steps to take in the index dimension between animation steps.
	:param min_speed: Minimum fps speed for animation.
	:param max_speed: Maximum fps speed for animation.
	:param speed_step: Step between different fps speeds on the speed slider.
	:param position: Position string for the time slider. Format: 'bottom/top'+'left/right'.
	"""

	_template = Template(
			"""
		{% macro script(this, kwargs) %}

			var times = {{this.times}};

			{{this._parent.get_name()}}.timeDimension = L.timeDimension(
				{times : times, currentTime: new Date(1)}
			);

			var {{ this.get_name() }} = new L.Control.TimeDimensionHeatmap(
				{{this.index | tojson}},
				{{ this.options | tojson(indent=20) }},
			).addTo({{this._parent.get_name()}});

		{% endmacro %}
		""".replace('\t', "    "),
			)

	default_js = [
			(
					"iso8601",
					"https://cdn.jsdelivr.net/npm/iso8601-js-period@0.2.1/iso8601.min.js",
					),
			(
					"leaflet.timedimension.min.js",
					"https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.min.js",
					),
			(
					"domdf_folium_tools_heatmap_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/heatmap.min.js",
					),
			]
	default_css = [
			(
					"leaflet.timedimension.control.min.css",
					"https://cdn.jsdelivr.net/npm/leaflet-timedimension@1.1.1/dist/leaflet.timedimension.control.css",
					),
			]

	def __init__(
			self,
			index: list,
			auto_play: bool = False,
			display_index: bool = True,
			index_steps: int = 1,
			min_speed: float = 0.1,
			max_speed: float = 10,
			speed_step: float = 0.1,
			position: Optional[TypePosition] = "bottomleft",
			):
		super().__init__(control="L.Control.TimeDimensionHeatmap", position=position)
		self._name = "TimeDimensionControl"

		self.index = index
		self.times = list(range(1, len(index) + 1))

		# TODO: use `parse_options`
		self.options = {
				"autoPlay": auto_play,
				"displayDate": display_index,
				"minSpeed": min_speed,
				"maxSpeed": max_speed,
				"position": cast(str, position),
				"speedStep": speed_step,
				"timeSteps": index_steps,
				"backwardButton": True,
				"forwardButton": True,
				"limitSliders": True,
				"limitMinimumRange": 5,
				"loopButton": True,
				"speedSlider": True,
				"timeSlider": True,
				"playButton": True,
				"playReverseButton": True,
				"timeSliderDragUpdate": False,
				"styleNS": "leaflet-control-timecontrol",
				}


class HeatMapWithTime(JSCSSMixin, Layer):
	"""
	Create a ``HeatMapWithTime`` layer.

	:param data: The points you want to plot. Nested list of points in the form ``[lat, lng]`` or ``[lat, lng, weight]``.
		The outer list corresponds to the various time steps in sequential order.
		Weight is in ``(0, 1]`` range and defaults to ``1`` if not specified for a point.
	:param data_variable: A variable to use for the data (e.g. loaded from an external file) rather than embedding the data directly.
	:param index: Index giving the label (or timestamp) of the elements of data.
		Should have the same length as data, or is replaced by a simple count if not specified.
	:param name: The name of the Layer, as it will appear in LayerControls.
	:param radius: The radius used around points for the heatmap.
	:param blur: Blur strength used for the heatmap. Must be between 0 and 1.
	:param min_opacity: The minimum opacity for the heatmap.
	:param max_opacity: The maximum opacity for the heatmap.
	:param scale_radius: Scale the radius of the points based on the zoom level.
	:param gradient: Mapping of point density values to colours.
		Colour can be a name (``'red'``), RGB values (``'rgb(255,0,0)'``) or a hex number (``'#FF0000'``).
	:param use_local_extrema: Defines whether the heatmap uses a global extrema set found from the input data
		OR a local extrema (the maximum and minimum of the currently displayed view).
	:param overlay: Adds the layer as an optional overlay (True) or the base layer (False).
	:param control: Whether the Layer will be included in LayerControls.
	:param show: Whether the layer will be shown on opening.
	"""

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{this.get_name()}} = new L.TDHeatmap(
				{{ this.data_variable }},
				{heatmapOptions: {{ this.options|tojson(indent=20) }}},
			);
		{% endmacro %}
		""".replace('\t', "    "),
			)

	default_js = [
			(
					"heatmap.min.js",
					"https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/pa7_hm.min.js",
					),
			(
					"leaflet-heatmap.js",
					"https://cdn.jsdelivr.net/gh/python-visualization/folium/folium/templates/pa7_leaflet_hm.min.js",
					),
			(
					"domdf_folium_tools_heatmap_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/heatmap.min.js",
					),
			]

	def __init__(
			self,
			data: list[list[Union[tuple[float, float, float], tuple[float, float]]]],
			data_variable: Optional[str] = None,
			index: Optional[list] = None,
			name: Optional[str] = None,
			radius: int = 15,
			blur: float = 0.8,
			min_opacity: float = 0,
			max_opacity: float = 0.6,
			scale_radius: bool = False,
			gradient: Optional[dict[float, str]] = None,
			use_local_extrema: bool = False,
			overlay: bool = True,
			control: bool = True,
			show: bool = True,
			):
		super().__init__(name=name, overlay=overlay, control=control, show=show)
		self._name = "HeatMap"

		# Input data.
		self.data = data
		self.data_variable = data_variable or json.dumps(data)
		self.index = (index if index is not None else [str(i) for i in range(1, len(data) + 1)])
		if len(self.data) != len(self.index):
			raise ValueError("Input data and index are not of compatible lengths.")  # noqa
		self.times = list(range(1, len(data) + 1))

		self.options = parse_options(
				radius=radius,
				blur=blur,
				min_opacity=min_opacity,
				max_opacity=max_opacity,
				scale_radius=scale_radius,
				use_local_extrema=use_local_extrema,
				default_weight=1,
				gradient=gradient,
				)

	# TODO: def _get_self_bounds(self) -> list[list[Optional[float]]]:
	# 	"""
	# 	Computes the bounds of the object itself (not including its children) in the form ``[[lat_min, lon_min], [lat_max, lon_max]]``.
	# 	"""

	# 	bounds = [[None, None], [None, None]]
	# 	for point in self.data:
	# 		bounds = [
	# 				[
	# 						none_min(bounds[0][0], point[0]),
	# 						none_min(bounds[0][1], point[1]),
	# 						],
	# 				[
	# 						none_max(bounds[1][0], point[0]),
	# 						none_max(bounds[1][1], point[1]),
	# 						],
	# 				]
	# 	return bounds


class HeatLayerWithTime(JSCSSMixin, Layer):
	"""
	Create a ``HeatLayerWithTime`` layer.

	:param data: The points you want to plot. Nested list of points in the form ``[lat, lng]``.
		The outer list corresponds to the various time steps in sequential order.
	:param data_variable: A variable to use for the data (e.g. loaded from an external file) rather than embedding the data directly.
	:param index: Index giving the label (or timestamp) of the elements of data.
		Should have the same length as data, or is replaced by a simple count if not specified.
	:param name: The name of the Layer, as it will appear in LayerControls.
	:param radius: The radius used around points for the heatmap.
	:param blur: Blur strength used for the heatmap. Must be between 0 and 1.
	:param min_opacity: The minimum opacity for the heatmap.
	:param gradient: Mapping of point density values to colours.
		Colour can be a name (``'red'``), RGB values (``'rgb(255,0,0)'``) or a hex number (``'#FF0000'``).
	:param overlay: Adds the layer as an optional overlay (True) or the base layer (False).
	:param control: Whether the Layer will be included in LayerControls.
	:param show: Whether the layer will be shown on opening.
	"""

	def __init__(
			self,
			data: list[list[tuple[float, float]]],
			data_variable: Optional[str] = None,
			index: Optional[list] = None,
			name: Optional[str] = None,
			radius: int = 25,
			blur: float = 15,
			min_opacity: float = 0.05,
			# max_opacity: float = 0.6,
			gradient: Optional[dict[float, str]] = None,
			overlay: bool = True,
			control: bool = True,
			show: bool = True,  # TODO: max
			):
		super().__init__(name=name, overlay=overlay, control=control, show=show)
		self._name = "HeatLayer"

		# Input data.
		self.data = data
		self.data_variable = data_variable or json.dumps(data)
		self.index = (index if index is not None else [str(i) for i in range(1, len(data) + 1)])
		if len(self.data) != len(self.index):
			raise ValueError("Input data and index are not of compatible lengths.")  # noqa
		self.times = list(range(1, len(data) + 1))

		self.options = parse_options(
				radius=radius,
				blur=blur,
				min_opacity=min_opacity,
				# max_opacity=max_opacity,
				gradient=gradient,
				)

	default_js = [
			(
					"leaflet-heat.js",
					"https://cdn.jsdelivr.net/gh/leaflet/Leaflet.heat@0.2.0/dist/leaflet-heat.js",
					),
			(
					"domdf_folium_tools_heatmap_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/heatmap.min.js",
					),
			]

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			var {{this.get_name()}} = new L.TDHeatLayer(
				{{ this.data_variable }},
				{heatmapOptions: {{ this.options|tojson }}
			});
		{% endmacro %}
		""".replace('\t', "    "),
			)
