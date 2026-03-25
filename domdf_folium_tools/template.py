#!/usr/bin/env python3
#
#  template.py
"""
Folium/Branca/Jinja2 template helpers.
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
from typing import TYPE_CHECKING

# 3rd party
from folium.template import Template

if TYPE_CHECKING:
	# 3rd party
	from jinja2.environment import TemplateModule

__all__ = ["SubclassingTemplate"]


class SubclassingTemplate(Template):
	"""
	Custom branca/folium template allowing for subclassing.

	:param source: The template source.
	:param base_template: The template "base class"
	"""

	base_template: Template

	def __new__(cls, source: str, base_template: Template):  # noqa: D102
		self = super().__new__(cls, source)
		self.base_template = base_template
		return self

	@property
	def module(self) -> "TemplateModule":  # noqa: D102
		template_module = super().module
		module_dict = template_module.__dict__

		for macro in {"html", "header", "script"}:
			if module_dict.get(macro, None) is None:
				module_dict[macro] = self.base_template.module.__dict__.get(macro, None)

		return template_module
