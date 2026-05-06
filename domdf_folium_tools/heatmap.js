/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
*  MIT Licenced
*/

var TDHeatmap = L.TimeDimension.Layer.extend({

	initialize: function(data, options) {
		var heatmapCfg = {
			radius: 15,
			blur: 0.8,
			maxOpacity: 1.,
			scaleRadius: false,
			useLocalExtrema: false,
			latField: 'lat',
			lngField: 'lng',
			valueField: 'count',
			defaultWeight: 1,
			...options.heatmapOptions || {},
		};
		var layer = new HeatmapOverlay(heatmapCfg);  // TODO: allow class to be overridden
		L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
		this._currentLoadedTime = 0;
		this._currentTimeData = {
			data: [],
		};
		this.data = data;
		this.defaultWeight = heatmapCfg.defaultWeight || 1;
	},

	onAdd: function(map) {
		L.TimeDimension.Layer.prototype.onAdd.call(this, map);
		map.addLayer(this._baseLayer);
		if (this._timeDimension) {
			this._getDataForTime(this._timeDimension.getCurrentTime());
		}
	},

	_onNewTimeLoading: function(ev) {
		this._getDataForTime(ev.time);
		return;
	},

	isReady: function(time) {
		return (this._currentLoadedTime == time);
	},

	_update: function() {
		this._baseLayer.setData(this._currentTimeData);
		return true;
	},

	_getDataForTime: function(time) {
		delete this._currentTimeData.data;
		this._currentTimeData.data = [];
		console.log('time=', time);
		// var data = this.data[time-1];
		var data = Array.prototype.concat(...this.data.slice(0, time));
		for (var i = 0; i < data.length; i++) {
			this._currentTimeData.data.push({
				lat: data[i][0],
				lng: data[i][1],
				count: data[i].length > 2 ? data[i][2] : this.defaultWeight,
			});
		}
		this._currentLoadedTime = time;
		if (this._timeDimension && time == this._timeDimension.getCurrentTime() && !this._timeDimension.isLoading()) {
			this._update();
		}
		this.fire('timeload', {
			time: time,
		});
	},

});

var TDHeatLayer = TDHeatmap.extend({

	initialize: function(data, options) {
		var heatmapCfg = {
			minOpacity: 0.05,
			maxZoom: 18,
			radius: 25,
			blur: 15,
			max: 1.0,
			...options.heatmapOptions || {},
		};
		var layer = new L.HeatLayer([], heatmapCfg);
		L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
		this._currentLoadedTime = 0;
		this._currentTimeData = {
			data: [],
		};
		this.data = data;
	},

	_update: function() {
		console.log(this._currentTimeData.data);
		this._baseLayer.setLatLngs(this._currentTimeData.data);
		return true;
	},

});

L.Control.TimeDimensionCustom = L.Control.TimeDimension.extend({

	initialize: function(index, options) {
		options.playerOptions = {
			buffer: 1,
			minBufferReady: -1,
			...options.playerOptions || {},
		};
		L.Control.TimeDimension.prototype.initialize.call(this, options);
		this.index = index;
	},

	_getDisplayDateFormat: function(date) {
		return this.index[date.getTime() - 1];
	},

});
