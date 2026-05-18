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
from typing import Any, Optional, TypeVar, Union

# 3rd party
from folium import Control, MacroElement
from folium.elements import JSCSSMixin
from folium.map import Layer
from folium.template import Template
from folium.utilities import TypePosition, parse_options

# this package
from domdf_folium_tools import __version__

__all__ = [
		"HeatLayerWithTime",
		"HeatMapWithTime",
		"TimeDimensionControl",
		"TimeDimensionState",
		"validate_input_data"
		]

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
	:param to_start_button: Whether to show the go to start button.
	:param to_end_button: Whether to show the go to end button.
	:param backward_button: Whether to show the button to go to the previous time step.
	:param forward_button: Whether to show the button to go to the next time step.
	:param play_button: Whether to show the play button.
	:param play_reverse_button: Whether to show the play backwards button.
	:param loop_button: Whether to show the button to loop the playback.
	:param time_slider: Whether to show the time slider.
	:param time_slider_drag_update:
	:param limit_sliders:
	:param limit_minimum_range:
	:param speed_slider: Whether to show the playback speed slider.
	"""

	control_class_name = "new L.Control.TimeDimensionHeatmap"

	_template = Template(
			"""
		{% macro header(this, kwargs) %}
		<style>
			.leaflet-bar-timecontrol .leaflet-control-timecontrol::before {
				font-family: unset;
			}

			.timecontrol-speed::before {
				font-family: "Font Awesome 6 Free" !important;
				content: var(--fa);
			}

			.fa-flipx::before {
				transform: rotate(180deg);
			}
		</style>
		{% endmacro %}
		{% macro script(this, kwargs) %}

			var times = {{this.times}};

			{{ this._parent.get_name() }}.timeDimension = L.timeDimension(
				{times : times, currentTime: new Date(1)}
			);

			var {{ this.get_name() }} = {{ this.control_class_name }}(
				{{ this.index | tojson }},
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
			(
					"fontawesome_css",
					"https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/css/all.min.css",
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
			to_start_button: bool = False,
			to_end_button: bool = False,
			backward_button: bool = True,
			forward_button: bool = True,
			play_button: bool = True,
			play_reverse_button: bool = True,
			loop_button: bool = True,
			time_slider: bool = True,
			time_slider_drag_update: bool = False,
			limit_sliders: bool = True,
			limit_minimum_range: int = 5,
			speed_slider: bool = True,
			):
		super().__init__(control=self.control_class_name, position=position)
		self._name = "TimeDimensionControl"

		self.index = index
		self.times = list(range(1, len(index) + 1))

		self.options = parse_options(
				auto_play=auto_play,
				display_date=display_index,
				min_speed=min_speed,
				max_speed=max_speed,
				position=position,
				speed_step=speed_step,
				time_steps=index_steps,
				to_start_button=to_start_button,
				to_end_button=to_end_button,
				backward_button=backward_button,
				forward_button=forward_button,
				limit_sliders=limit_sliders,
				limit_minimum_range=limit_minimum_range,
				loop_button=loop_button,
				speed_slider=speed_slider,
				time_slider=time_slider,
				play_button=play_button,
				play_reverse_button=play_reverse_button,
				time_slider_drag_update=time_slider_drag_update,
				)

		self.options["styleNS"] = "leaflet-control-timecontrol"


HeatmapDataWeighted = list[list[Union[tuple[float, float, float], tuple[float, float]]]]
HeatLayerData = list[list[tuple[float, float]]]

_D = TypeVar("_D", HeatmapDataWeighted, HeatLayerData)


def validate_input_data(data: _D, index: Optional[list] = None) -> tuple[_D, list]:
	"""
	Ensures the data and the index are the same length.

	:param data: The points you want to plot. Nested list of points in the form ``[lat, lng]`` or ``[lat, lng, weight]``.
		The outer list corresponds to the various time steps in sequential order.
		Weight is in ``(0, 1]`` range.
	:param index: Index giving the label (or timestamp) of the elements of data.
		Should have the same length as data, or is replaced by a simple count if not specified.
	"""

	# TODO: check for other issues

	index = (index if index is not None else [str(i) for i in range(1, len(data) + 1)])

	if len(data) != len(index):
		raise ValueError("Input data and index are not of compatible lengths.")

	return data, index


_heatmap_template = Template(
		"""
		{% macro script(this, kwargs) %}
			var {{ this.get_name() }} = {{ this.layer_class_name }}(
				{{ this.data_variable }},
				{heatmapOptions: {{ this.options|tojson(indent=20) }}},
			);
		{% endmacro %}
		""".replace('\t', "    "),
		)


class HeatMapWithTime(JSCSSMixin, Layer):
	"""
	Create a ``HeatMapWithTime`` layer.

	:param data: The points you want to plot. Nested list of points in the form ``[lat, lng]`` or ``[lat, lng, weight]``.
		The outer list corresponds to the various time steps in sequential order.
		Weight is in ``(0, 1]`` range and defaults to ``default_weight`` (or ``1``) if not specified for a point.
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
	:param default_weight: Default weight for datapoints if not specified in ``data``.
	:param overlay: Adds the layer as an optional overlay (True) or the base layer (False).
	:param control: Whether the Layer will be included in LayerControls.
	:param show: Whether the layer will be shown on opening.

	.. note::

		If omitting ``data`` to load it from an external file etc. it is advisable to call :func:`~.validate_input_data`
		on the data and index values to avoid common pitfalls. ``data_variable`` and ``index`` must also be provided and cannot be :py:obj:`None`.
	"""

	layer_class_name = "new L.TDHeatmap"
	_template = _heatmap_template

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
			data: Optional[HeatmapDataWeighted],
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
			default_weight: float = 1.0,
			overlay: bool = True,
			control: bool = True,
			show: bool = True,
			):
		super().__init__(name=name, overlay=overlay, control=control, show=show)
		self._name = "HeatMap"

		# Input data.
		if data is None:
			if not data_variable:
				raise ValueError("'data_variable' was not specified and 'data' was set to None")
			if not index:
				raise ValueError("'index' was not specified and 'data' was set to None")

			self.data_variable = data_variable
			self.index = index
		else:
			data, self.index = validate_input_data(data, index)
			self.data_variable = data_variable or json.dumps(data)

		self.times = list(range(1, len(self.index) + 1))

		self.options = parse_options(
				radius=radius,
				blur=blur,
				min_opacity=min_opacity,
				max_opacity=max_opacity,
				scale_radius=scale_radius,
				use_local_extrema=use_local_extrema,
				default_weight=default_weight,
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

	.. note::

		If omitting ``data`` to load it from an external file etc. it is advisable to call :func:`~.validate_input_data`
		on the data and index values to avoid common pitfalls. ``data_variable`` and ``index`` must also be provided and cannot be :py:obj:`None`.
	"""

	layer_class_name = "new L.TDHeatLayer"
	_template = _heatmap_template

	def __init__(
			self,
			data: Optional[HeatLayerData],
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
		if data is None:
			if not data_variable:
				raise ValueError("'data_variable' was not specified and 'data' was set to None")
			if not index:
				raise ValueError("'index' was not specified and 'data' was set to None")

			self.data_variable = data_variable
			self.index = index
		else:
			data, self.index = validate_input_data(data, index)
			self.data_variable = data_variable or json.dumps(data)

		self.times = list(range(1, len(self.index) + 1))

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


class TimeDimensionState(MacroElement):
	"""
	Inject JavaScript to track and set overlay layers from URL parameter.

	Add to map after adding the time dimension control.

	:param time_dimension_control: The time dimension control element.
	:param default_time: The defualt start time if not specified in the URL.
	:param param_name: The URL query parameter to use.
	"""

	default_js = [
			(
					"domdf_folium_tools_heatmap_js",
					f"https://cdn.jsdelivr.net/gh/domdfcoding/domdf-folium-tools@v{__version__}/domdf_folium_tools/heatmap.min.js",
					),
			]

	_template = Template(
			"""
		{% macro script(this, kwargs) %}
			const timeDimensionState = new L.TimeDimensionState({{this._parent.get_name()}}, {{this.time_dimension_control.get_name()}}.index, {{this.param_name|tojson}})
			timeDimensionState.fromURL({{this.default_time}})
			timeDimensionState.setup();
		{% endmacro %}
		""".replace('\t', "    "),
			)

	def __init__(
			self,
			time_dimension_control: TimeDimensionControl,
			default_time: Optional[Any] = None,
			param_name: str = "time",
			):
		super().__init__()
		self._name = "TimeDimensionState"
		self.time_dimension_control = time_dimension_control
		self.param_name = param_name

		if default_time is None:
			self.default_time = time_dimension_control.index[0]
		else:
			self.default_time = default_time
