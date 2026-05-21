/**
 * A Leaflet Marker which also adds a polygon (or polygons).
 *
 * If the marker is removed (manually or via a markercluster) the polygon is removed too.
 *
 * @param latlng The coordinates of the marker.
 * @param polyPoints Array of arrays giving coordinates of the polygon(s) points.
 * @param options Standard L.Marker options.
 */
export const PolyMarker = L.Marker.extend({
	// TODO: highlight polygon when marker clicked
	initialize: function(
		latlng: L.LatLng,
		polyPoints: L.LatLngExpression[][],
		options: L.MarkerOptions,
		polygonOptions?: L.PolylineOptions,
	) {
		// @ts-expect-error  // Thinks initialize doesn't exist but it does
		L.Marker.prototype.initialize.call(this, latlng, options);
		this._polygons = [];

		if (!polygonOptions) {
			polygonOptions = {};
		}

		if (polyPoints) {
			polyPoints.forEach((p: L.LatLngExpression[]) => {
				if (options.icon) {
					if ('markerColor' in options.icon.options) {
						// @ts-expect-error  // Doesn't know about extra markers
						const markerColour: string = options.icon.options.markerColor;
						polygonOptions.color = markerColour;
					}
				}
				this._polygons.push(L.polygon(p, polygonOptions));
			});
		}
	},

	onAdd: function(map: L.Map) {
		console.log('Add polygons', this._polygons);
		L.Marker.prototype.onAdd.call(this, map);
		if (this._polygons) {
			this._polygons.forEach((p: L.Polygon) => {
				p.addTo(map);
			});
		}

		return this;
	},

	onRemove: function(map: L.Map) {
		// TODO: if marker removed because offscreen the polygon goes too!
		console.log('Remove polygons', this._polygons);
		L.Marker.prototype.onRemove.call(this, map);
		if (this._polygons) {
			this._polygons.forEach((p: L.Polygon) => {
				p.remove();
			});
		}

		return this;
	},

	polygonsBindPopup: function(
		content: ((layer: L.Layer) => L.Content) | L.Content | L.Popup,
		options?: L.PopupOptions,
	) {
		this._polygons.forEach((p: L.Polygon) => {
			p.bindPopup(content, options);
		});
	},

	polygonsSetOptions: function(options: L.PolylineOptions) {
		this._polygons.forEach((p: L.Polygon) => {
			Object.assign(p.options, options);
		});
	},
});
