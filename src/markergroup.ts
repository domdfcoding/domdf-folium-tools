/**
 * A fake grouping of markers in a marker cluster.
 *
 * Allows markers to be shown/hidden with the layer control but maintaining a single MarkerClusterGroup underneath.
 *
 * @param cluster The Leaflet MarkerClusterGroup to add markers too.
 */
export const MarkerGroup = L.Layer.extend({
	initialize: function(cluster: typeof L.MarkerClusterGroup, _options?: L.LayerOptions) {
		console.log('Initialize called');
		// L.Layer.prototype.initialize.call(this, options);
		this._markers = [];
		this._marker_cluster = cluster;
	},

	/**
	 * Add layers (markers) to the group and to the actual marker cluster.
	 *
	 * @param layers The layers/markers to add.
	 * @param addToCluster Whether to add the markers to the marker cluster. Default true.
	 */
	addLayers: function(layers: L.Layer[], addToCluster: boolean = true) {
		if (this._map) {
			this._marker_cluster.addLayers(this.internLayer(layers, addToCluster));
		}
	},

	/**
	 * Like addLayers, adds to the internal list of markers but doesn't add to map.
	 *
	 * @param layers The layers/markers to add.
	 * @param addToCluster Whether to add the markers to the marker cluster. Default true.
	 *
	 * @returns The list of markers to add to the map (empty if the layer is not visible)
	 */
	/*
	*/
	internLayers: function(layers: L.Layer[], addToCluster: boolean = true) {
		// TODO: move this function to domdf-folium-tools
		this._markers.push(...layers);

		if (this._map && addToCluster) {
			return layers;
		}

		return [];
	},

	onRemove: function(_map: L.Map) {
		this._map = null;
		console.log('Removing markers', this._markers);
		// TODO: chunkedLoading not triggered. Is it supposed to?
		this._marker_cluster.removeLayers(this._markers);
		return this;
	},

	onAdd: function(map: L.Map) {
		this._map = map;
		if (this._markers !== undefined) {
			this._marker_cluster.addLayers(this._markers);
		}
		return this;
	},
});
