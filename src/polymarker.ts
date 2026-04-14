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
	initialize: function(latlng: L.LatLng, polyPoints: L.LatLngExpression[][], options: L.MarkerOptions) {
		// @ts-expect-error  // Thinks initialize doesn't exist but it does
		L.Marker.prototype.initialize.call(this, latlng, options);
		this._polygons = [];
		if (polyPoints) {
			polyPoints.forEach((p: L.LatLngExpression[]) => {
				let polygonOptions = {};
				if (options.icon) {
					if ('markerColor' in options.icon.options) {
						polygonOptions = { color: options.icon.options.markerColor };
					}
				}
				this._polygons.push(L.polygon(p, polygonOptions));
			});
		}
	},

	onAdd: function(map: L.Map) {
		console.log('Add polygon', this._polygon);
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
		console.log('Remove polygon', this._polygon);
		L.Marker.prototype.onRemove.call(this, map);
		if (this._polygons) {
			this._polygons.forEach((p: L.Polygon) => {
				p.remove();
			});
		}

		return this;
	},
});
