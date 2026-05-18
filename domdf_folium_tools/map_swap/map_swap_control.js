/*
 * AboutControl
 *
 * Leaflet control for displaying an about dialog (a Bootstrap modal).
 */
//
// Copyright © 2026 Dominic Davis-Foster <dominic@davis-foster.co.uk>
//
// Adapted from https://github.com/domoritz/leaflet-locatecontrol
// Copyright (c) 2016 Dominik Moritz
//
// Adapted from https://github.com/smeijer/leaflet-geosearch
// Copyright (c) 2010-2016 Stephan Meijer
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
// EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
// MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
// IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
// DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
// OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
// OR OTHER DEALINGS IN THE SOFTWARE.
//

// TODO: generate from typescript

/**
 * Create a DOM element with a class name and optionally append it to a parent.
 * @param {string} tag - The element tag name.
 * @param {string} [className] - Space-separated class names.
 * @param {HTMLElement} [parent] - Optional parent to append the element to.
 * @returns {HTMLElement}
 */
function createElement(tag, className, parent) {
	const el = document.createElement(tag);
	if (className) el.className = className;
	parent?.append(el);
	return el;
}

/**
 * Shallow clone options to prevent prototype pollution.
 * Clones arrays and plain objects, keeps functions/classes as references.
 * @param {Object} options - The options object to clone.
 * @returns {Object} A shallow clone of the options object.
 */
function cloneOptions(options) {
	const cloned = {};
	for (const key in options) {
		const val = options[key];
		if (Array.isArray(val)) {
			cloned[key] = [...val];
		} else if (val?.constructor === Object) {
			cloned[key] = { ...val };
		} else {
			cloned[key] = val;
		}
	}
	return cloned;
}

const MapSwapControl = L.Control.extend({
	options: {
		/** Position of the control */
		position: 'topleft',
		/** The CSS class for the icon. For example 'fa-solid fa-map' */
		icon: 'fa-solid fa-map',
		/** The element to be created for icons. For example span or i */
		iconElementTag: 'span',

		// TODO: options for target and tooltip

		/**
		 * This callback can be used in case you would like to override button creation behavior.
		 * This is useful for DOM manipulation frameworks such as angular etc.
		 * This function should return an object with HtmlElement for the button (link property) and the icon (icon property).
		 */
		createButtonCallback(container, options) {
			const link = createElement('a', 'leaflet-bar-part leaflet-bar-part-single', container);
			link.title = 'Go to a different map';
			link.href = '#';
			link.setAttribute('role', 'button');
			link.setAttribute('aria-label', link.title);
			const icon = createElement(options.iconElementTag, options.icon, link);
			icon.classList.add('leaflet-map-swap-icon');

			return { link, icon };
		},
	},

	onClick(event) {
		console.log('Clicked', this._container.classList.contains('active'));
		event.preventDefault();
		event.stopPropagation();

		if (this._container.classList.contains('active')) {
			this.close();
		} else {
			this.open();
		}
	},

	open() {
		this._container.classList.add('active');
		this._form.querySelector('a').focus();
	},

	close() {
		this._container.classList.remove('active');
	},

	initialize(options = {}) {
		// Clone default options to prevent prototype pollution
		this.options = cloneOptions(this.options);

		// Merge user-provided options
		for (const key in options) {
			const userVal = options[key];
			const defaultVal = this.options[key];
			if (userVal?.constructor === Object && defaultVal?.constructor === Object) {
				Object.assign(defaultVal, userVal);
			} else {
				this.options[key] = userVal;
			}
		}
	},

	/**
	 * Add control to map. Returns the container for the control.
	 */
	onAdd(map) {
		const container = createElement('div',
			'leaflet-control-map-swap leaflet-bar leaflet-control leaflet-map-swap-button');
		this._container = container;
		this._map = map;

		this._form = createElement('div', 'map-swap-links px-2 py-1', container);

		const header = createElement('span', 'ms-1', this._form);
		header.innerHTML = 'Go To Map';

		for (const [map, target] of Object.entries(this.options.maps)) {
			const button = createElement('a', 'border rounded my-1 text-start', this._form);
			button.role = 'button';
			button.href = target;
			function handleClick(e) {
				const url = new URL(button.href, window.location.href);
				for (let [k, v] of new URLSearchParams(window.location.search).entries()) {
					url.searchParams.set(k, v);
				}
				button.href = url.toString();
				e.href = url.toString();
				console.log(e.href);
			}
			button.addEventListener('click', (e) => {
				handleClick(e);
				// e.preventDefault()
				// e.stopPropagation()
			});
			button.addEventListener('auxclick', (e) => {
				handleClick(e);
				// e.preventDefault()
				// e.stopPropagation()
			});
			button.innerHTML = map;
		}

		const linkAndIcon = this.options.createButtonCallback(container, this.options);
		this._link = linkAndIcon.link;
		this._icon = linkAndIcon.icon;

		this._link.addEventListener('click', (e) => this.onClick(e));
		this._link.addEventListener('dblclick', (e) => {
			e.preventDefault();
			e.stopPropagation();
		});

		return container;
	},
});

function mapSwapControl(options) {
	return new MapSwapControl(options);
}
