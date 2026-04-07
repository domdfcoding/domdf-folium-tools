#!/usr/bin/env python3
#
#  __init__.py
"""
Miscellaneous utilities for folium/leaflet.
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
from random import Random
from typing import Any, Literal, TypedDict, Union

# 3rd party
import folium
from folium.template import Template

__all__ = ["Coordinates", "FeatureCollection", "embed_styles", "set_branca_random_seed"]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2026 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.0b4"
__email__: str = "dominic@davis-foster.co.uk"


def set_branca_random_seed(seed: Union[str, int]) -> None:
	"""
	Use a fixed random number generator seed for branca (affects element IDs e.g. folium's ``map_{id}``).

	:param seed:
	"""

	# 3rd party
	from branca import element

	rand = Random(seed)

	def urandom(size: int) -> bytes:
		return rand.randbytes(size)

	element.urandom = urandom


def embed_styles(m: folium.Map, custom_css: str) -> folium.Element:
	"""
	Embed the map's custom CSS into the HTML.

	:param m:
	:param custom_css: CSS as a string.
	"""

	class EmbeddedStyles(folium.MacroElement):
		_template = Template(
				f"""
			{{% macro header(this, kwargs) %}}
				<style>
					{custom_css}
				</style>
			{{% endmacro %}}
	""",
				)

	return EmbeddedStyles().add_to(m)


class Coordinates(TypedDict):
	"""
	Coordinates as a dictionary.
	"""

	latitude: float
	longitude: float


class FeatureCollection(TypedDict):
	"""
	Represents a GeoJSON feature collection.
	"""

	type: Literal["FeatureCollection"]
	features: list[Any]  # TODO: type
