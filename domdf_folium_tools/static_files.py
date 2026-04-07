#!/usr/bin/env python3
#
#  static_files.py
"""
Utilities for static CSS and JS.
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
import shutil
from collections.abc import Iterable
from typing import NamedTuple, Union

# 3rd party
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.typing import PathLike

__all__ = ["FileOnDisk", "PythonResource", "copy_resource", "copy_static_files"]


def copy_resource(module: str, filename: str, target_dir: PathPlus) -> None:
	"""
	Copy the given resource from the given Python module to the given directory.

	:param module:
	:param filename:
	:param target_dir:
	"""

	(target_dir / filename).write_text(importlib_resources.read_text(module, filename))


class PythonResource(NamedTuple):
	"""
	Represents a resource in a Python module.
	"""

	module: str
	filename: str


class FileOnDisk(NamedTuple):
	"""
	Represents a local file on disk.
	"""

	filename: PathLike


def _copy_files(files: Iterable[Union[PythonResource, FileOnDisk]], destination: PathPlus) -> None:
	for file in files:
		if isinstance(file, PythonResource):
			copy_resource(file.module, file.filename, destination)
		elif isinstance(file, FileOnDisk):
			shutil.copy2(file.filename, destination)
		else:
			raise NotImplementedError(type(file), file)


def copy_static_files(
		static_dir: PathLike,
		js_files: Iterable[Union[PythonResource, FileOnDisk]],
		css_files: Iterable[Union[PythonResource, FileOnDisk]],
		) -> None:
	"""
	Copy CSS and JS files into the given directory.

	:param static_dir:
	:param js_files:
	:param css_files:
	"""

	static_dir = PathPlus(static_dir)
	js_files = list(js_files)
	css_files = list(css_files)

	js_dir = static_dir / "js"
	css_dir = static_dir / "css"

	if js_files:
		js_dir.maybe_make(parents=True)

		_copy_files(js_files, js_dir)

	if css_files:
		css_dir.maybe_make(parents=True)

		_copy_files(css_files, css_dir)
