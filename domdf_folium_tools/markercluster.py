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
from typing import Any, Optional

# 3rd party
from folium.plugins import MarkerCluster as FoliumMarkerCluster
from folium.template import Template

__all__ = ["MarkerCluster"]


class MarkerCluster(FoliumMarkerCluster):
	r"""
	Customised MarkerCluster plugin with support for ``chunkProgress`` and ``maxClusterRadius`` functions.

	:param \*args: Positional arguments for the oricinal ``MarkerCluster`` class.
	:param chunk_progress_function: Name of the javascript function for the ``chunkProgress`` option.
	:param max_cluster_radius_function: Name of the javascript function for the ``maxClusterRadius`` option.
	:param \*\*kwargs: Keyword arguments for the oricinal ``MarkerCluster`` class.
	"""

	# TODO: params in docstring

	_template = Template(
			"""
        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.markerClusterGroup(
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
