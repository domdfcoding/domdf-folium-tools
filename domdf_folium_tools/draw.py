#!/usr/bin/env python3
#
#  draw.py
"""
Plugin for drawing lines, curves and polygons on the map.
"""
#
#  Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/draw.py
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
from typing import Any, Optional

# 3rd party
from folium import FeatureGroup, MacroElement
from folium.elements import JSCSSMixin
from folium.template import Template

__all__ = ["CurveDraw"]


class CurveDraw(JSCSSMixin, MacroElement):
	"""
	Vector drawing and editing plugin for Leaflet.

	:param export: Add a small button that exports the drawn shapes to JSON.
	:param feature_group: The ``FeatureGroup`` object that will hold the editable figures.
		This can be used to initialize the Draw plugin with predefined Layer objects.
	:param filename: Name of the export JSON file.
	:param position: Position of control.
		See https://leafletjs.com/reference.html#control
	:param draw_options: The options used to configure the draw toolbar.
		See http://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html#drawoptions
	:param edit_options: The options used to configure the edit toolbar.
		See https://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html#editpolyoptions
	:param on: Event handlers to attach to the created layer.
		Pass a mapping from the names of the events to their ``JsCode`` handlers.

	For more info see https://leaflet.github.io/Leaflet.draw/docs/leaflet-draw-latest.html
	"""

	default_js = [
			("tween_js", "https://cdnjs.cloudflare.com/ajax/libs/tween.js/17.2.0/Tween.min.js"),
			(
					"leaflet_curve_js",
					"https://cdn.jsdelivr.net/npm/@elfalem/leaflet-curve@0.9.2/dist/leaflet.curve.min.js",
					),
			(
					"leaflet_draw_js",
					"https://cdn.jsdelivr.net/gh/domdfcoding/Leaflet.draw@curve_built/dist/leaflet.draw.js",
					),
			]
	default_css = [
			(
					"leaflet_draw_css",
					"https://cdn.jsdelivr.net/gh/qpincon/Leaflet.draw@curve_built/dist/leaflet.draw.css",
					),
			]

	_template = Template(
			"""
  {% macro html(this, kwargs) %}
			{% if this.export %}
			<style>
				#export {
					position: absolute;
					top: 5px;
					right: 10px;
					z-index: 999;
					background: white;
					color: black;
					padding: 6px;
					border-radius: 4px;
					cursor: pointer;
					font-size: 12px;
					text-decoration: none;
					top: 90px;
				}
			</style>
			<a href='#' id='export'>Export</a>
			{% endif %}
		{% endmacro %}

		{% macro script(this, kwargs) %}
			var options = {
			  position: {{ this.position|tojson }},
			  draw: {{ this.draw_options|tojson }},
			  edit: {{ this.edit_options|tojson }},
			}
			{%- if this.feature_group  %}
				var drawnItems_{{ this.get_name() }} =
					{{ this.feature_group.get_name() }};
			{%- else %}
				// FeatureGroup is to store editable layers.
				var drawnItems_{{ this.get_name() }} =
					new L.featureGroup().addTo(
						{{ this._parent.get_name() }}
					);
			{%- endif %}

			options.edit.featureGroup = drawnItems_{{ this.get_name() }};
			var {{ this.get_name() }} = new L.Control.Draw(
				options
			).addTo( {{this._parent.get_name()}} );
			{{ this._parent.get_name() }}.on(L.Draw.Event.CREATED, function(e) {
				var layer = e.layer;

				{%- for event, handler in this.on.items()   %}
				layer.on(
					"{{event}}",
					{{handler}}
				);
				{%- endfor %}
				drawnItems_{{ this.get_name() }}.addLayer(layer);
			});

			{% if this.export %}
			document.getElementById('export').onclick = function(e) {
				var data = [];
				drawnItems_{{ this.get_name() }}.getLayers().forEach((l) => {
					if (l instanceof L.Curve) {
						data.push(["curve", l.getLatLngs()])
					} else if (l instanceof L.Rectangle) {
						data.push(["rectangle", l.getLatLngs()])
					} else if (l instanceof L.Polygon) {
						data.push(["polygon", l.getLatLngs()])
					} else if (l instanceof L.Polyline) {
						data.push(["polyline", l.getLatLngs()])
					}
					// All we care about for now

				})
				var convertedData = 'text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(data));
				document.getElementById('export').setAttribute(
					'href', 'data:' + convertedData
				);
				document.getElementById('export').setAttribute(
					'download', {{ this.filename|tojson }}
				);
			}
			{% endif %}
		{% endmacro %}
		""",
			)

	def __init__(
			self,
			export: bool = False,
			feature_group: Optional[FeatureGroup] = None,
			filename: str = "data.json",
			position: str = "topleft",
			draw_options: Optional[dict[str, Any]] = None,
			edit_options: Optional[dict[str, Any]] = None,
			on: Optional[dict[str, Any]] = None,
			):
		super().__init__()
		self._name = "CurveDrawControl"
		self.export = export
		self.feature_group = feature_group
		self.filename = filename
		self.position = position
		self.draw_options = draw_options or {}
		self.edit_options = edit_options or {}
		self.on = on or {}
