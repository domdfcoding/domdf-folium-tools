/**
 * A fake grouping of markers in a marker cluster.
 *
 * Allows markers to be shown/hidden with the layer control but maintaining a single MarkerClusterGroup underneath.
 *
 * @param cluster The Leaflet MarkerClusterGroup to add markers too.
 */
export const MarkerGroup = L.Layer.extend({
	initialize: function (cluster: typeof L.MarkerClusterGroup, _options?: L.LayerOptions) {
		console.log('Initialize called');
		// L.Layer.prototype.initialize.call(this, options);
		this._markers = [];
		this._marker_cluster = cluster;
	},

	addLayers: function (layers: L.Layer[]) {
		this._markers.push(...layers);

		if (this._map) {
			// Don't add if the layer isn't visible
			this._marker_cluster.addLayers(layers);
		}
	},

	onRemove: function (_map: L.Map) {
		this._map = null;
		console.log('Removing markers', this._markers);
		// TODO: chunkedLoading not triggered. Is it supposed to?
		this._marker_cluster.removeLayers(this._markers);
		return this;
	},

	onAdd: function (map: L.Map) {
		this._map = map;
		if (this._markers !== undefined) {
			this._marker_cluster.addLayers(this._markers);
		}
		return this;
	}
});
