#!/usr/bin/env python3
#
#  favicon.py
"""
Add HTML tag for browser favicon.

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/rel#icon
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
import base64

# 3rd party
import folium
from folium.template import Template

__all__ = ["HrefFavicon", "SVGFavicon", "base64_encode"]


def base64_encode(value: str) -> str:
	"""
	Encode the given string as base64.

	:param value:
	"""

	return base64.b64encode(value.encode("utf-8")).decode("utf-8")


class SVGFavicon(folium.MacroElement):
	"""
	Add an SVG image as the favicon.

	:param svg:
	"""

	# TODO: apple-touch-icon and apple-touch-startup-image

	_template = Template(
			"""
{% macro header(this, kwargs) %}
	<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{{ this.svg }}">
{% endmacro %}
""",
			)

	def __init__(self, svg: str):
		super().__init__()
		self.svg = base64_encode(svg)


class HrefFavicon(folium.MacroElement):
	"""
	Add an image from a URL as the favicon.

	:param url:
	"""

	_template = Template(
			"""
{% macro header(this, kwargs) %}
	<link rel="icon" href="{{ this.href }}">
	<link rel="apple-touch-icon" href="{{ this.href }}">
	<link rel="apple-touch-startup-image" href="{{ this.href }}">
{% endmacro %}
""",
			)

	def __init__(self, url: str):
		super().__init__()
		self.href = url
