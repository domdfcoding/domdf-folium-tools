/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
*
*  Based on https://github.com/socib/Leaflet.TimeDimension/master/src/leaflet.timedimension.control.js
*  Copyright (c) 2014 ICTS SOCIB - Servei d'observació i predicció costaner de les Illes Balears.
*
*  MIT Licenced
*/

export type HeatmapOptions = {
	heatmapOptions: object | null | undefined;
};

// @ts-expect-error  // No types for TimeDimension
export const TDHeatmap = L.TimeDimension.Layer.extend({
	initialize: function(data: number[][], options: HeatmapOptions) {
		const heatmapCfg = {
			radius: 15,
			blur: 0.8,
			maxOpacity: 1,
			scaleRadius: false,
			useLocalExtrema: false,
			latField: 'lat',
			lngField: 'lng',
			valueField: 'count',
			defaultWeight: 1,
			...options.heatmapOptions || {},
		};

		// @ts-expect-error  // No types for HeatmapOverlay
		const layer = new HeatmapOverlay(heatmapCfg); // TODO: allow class to be overridden

		// @ts-expect-error  // No types for TimeDimension
		L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);

		this._currentLoadedTime = 0;
		this._currentTimeData = {
			data: [],
		};
		this.data = data;
		this.defaultWeight = heatmapCfg.defaultWeight || 1;
	},

	onAdd: function(map: L.Map) {
		// @ts-expect-error  // No types for TimeDimension
		L.TimeDimension.Layer.prototype.onAdd.call(this, map);

		map.addLayer(this._baseLayer);
		if (this._timeDimension) {
			this._getDataForTime(this._timeDimension.getCurrentTime());
		}
	},

	// @ts-expect-error  // TODO
	_onNewTimeLoading: function(ev) {
		this._getDataForTime(ev.time);
	},

	isReady: function(time: number) {
		return (this._currentLoadedTime === time);
	},

	_update: function() {
		this._baseLayer.setData(this._currentTimeData);
		return true;
	},

	_getDataForTime: function(time: number) {
		delete this._currentTimeData.data;
		this._currentTimeData.data = [];
		console.log('time=', time);
		// const data = this.data[time-1];
		const data = Array.prototype.concat(...this.data.slice(0, time));

		for (let i = 0; i < data.length; i++) {
			this._currentTimeData.data.push({
				lat: data[i][0],
				lng: data[i][1],
				count: data[i].length > 2 ? data[i][2] : this.defaultWeight,
			});
		}

		this._currentLoadedTime = time;
		if (this._timeDimension && time === this._timeDimension.getCurrentTime() && !this._timeDimension.isLoading()) {
			this._update();
		}

		this.fire('timeload', { time });
	},
});

export const TDHeatLayer = TDHeatmap.extend({
	initialize: function(data: number[][], options: HeatmapOptions) {
		const heatmapCfg = {
			minOpacity: 0.05,
			maxZoom: 18,
			radius: 25,
			blur: 15,
			max: 1.0,
			...options.heatmapOptions || {},
		};

		// @ts-expect-error  // No types for Leaflet.Heat
		const PatchedHeatLayer = L.HeatLayer.extend({
			redraw: function() {
				if (this._heat && !this._frame && this._map) {
					if (!this._map._animating) {
						this._frame = L.Util.requestAnimFrame(this._redraw, this);
					}
				}
				return this;
			},
		});

		const layer = new PatchedHeatLayer([], heatmapCfg);

		// @ts-expect-error  // No types for TimeDimension
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

export type TimeDimensionCustomOptions = {
	playerOptions: object | null | undefined;
};

// @ts-expect-error  // No types for TimeDimension
export const TimeDimensionControl = L.Control.TimeDimension.extend({
	initialize: function(index: object[], options: TimeDimensionCustomOptions) {
		options.playerOptions = {
			buffer: 1,
			minBufferReady: -1,
			...options.playerOptions || {},
		};

		// @ts-expect-error  // No types for TimeDimension
		L.Control.TimeDimension.prototype.initialize.call(this, options);

		this.index = index;
	},

	_getDisplayDateFormat: function(date: Date) {
		return this.index[date.getTime() - 1];
	},

	onAdd: function(map: L.Map) {
		this._map = map;

		// @ts-expect-error  // Doesn't know map.timeDimension exists.
		if (!this._timeDimension && map.timeDimension) {
			// @ts-expect-error  // Doesn't know map.timeDimension exists.
			this._timeDimension = map.timeDimension;
		}
		this._initPlayer();

		const container = L.DomUtil.create('div', 'leaflet-bar leaflet-bar-horizontal leaflet-bar-timecontrol');
		if (this.options.toStartButton) {
			this._buttomStart = this._createButton('ToStart', container);
			this._buttomStart.title = 'To Start';
			this._buttomStart.classList.add('fa-solid', 'fa-backward-fast');
		}
		if (this.options.backwardButton) {
			this._buttonBackward = this._createButton('Backward', container);
			this._buttonBackward.classList.add('fa-solid', 'fa-backward-step');
		}
		if (this.options.playReverseButton) {
			this._buttonPlayReversePause = this._createButton('Play Reverse', container);
			this._buttonPlayReversePause.classList.remove('reverse');
			this._buttonPlayReversePause.classList.add('fa-solid', 'fa-play', 'fa-flipx');
		}
		if (this.options.playButton) {
			this._buttonPlayPause = this._createButton('Play', container);
			this._buttonPlayPause.classList.add('fa-solid', 'fa-play');
		}
		if (this.options.forwardButton) {
			this._buttonForward = this._createButton('Forward', container);
			this._buttonForward.classList.add('fa-solid', 'fa-forward-step');
		}
		if (this.options.toEndButton) {
			this._buttomEnd = this._createButton('ToEnd', container);
			this._buttomEnd.title = 'To End';
			this._buttomEnd.classList.add('fa-solid', 'fa-forward-fast');
		}
		if (this.options.loopButton) {
			this._buttonLoop = this._createButton('Loop', container);
			this._buttonLoop.classList.add('fa-solid', 'fa-retweet');
		}
		if (this.options.displayDate) {
			this._displayDate = this._createButton('Date', container);
		}
		if (this.options.timeSlider) {
			this._sliderTime = this._createSliderTime(
				this.options.styleNS + ' timecontrol-slider timecontrol-dateslider',
				container,
			);
		}
		if (this.options.speedSlider) {
			this._sliderSpeed = this._createSliderSpeed(
				this.options.styleNS + ' timecontrol-slider timecontrol-speed',
				container,
			);
			this._sliderSpeed._container.parentElement.classList.add('fa-clock');
		}

		this._steps = this.options.timeSteps || 1;

		this._timeDimension.on('timeload', this._update, this);
		this._timeDimension.on('timeload', this._onPlayerStateChange, this);
		this._timeDimension.on('timeloading', this._onTimeLoading, this);

		this._timeDimension.on('limitschanged availabletimeschanged', this._onTimeLimitsChanged, this);

		L.DomEvent.disableClickPropagation(container);

		return container;
	},

	_onPlayerStateChange: function() {
		// @ts-expect-error  // No types for TimeDimension
		L.Control.TimeDimension.prototype._onPlayerStateChange.call(this);
		if (this._buttonPlayPause) {
			if (this._player.isPlaying() && this._player.getSteps() > 0) {
				L.DomUtil.removeClass(this._buttonPlayPause, 'pause');
				L.DomUtil.addClass(this._buttonPlayPause, 'fa-pause');
				L.DomUtil.removeClass(this._buttonPlayPause, 'fa-play');
			} else {
				L.DomUtil.removeClass(this._buttonPlayPause, 'play');
				L.DomUtil.removeClass(this._buttonPlayPause, 'fa-pause');
				L.DomUtil.addClass(this._buttonPlayPause, 'fa-play');
			}
		}
		if (this._buttonPlayReversePause) {
			L.DomUtil.removeClass(this._buttonPlayReversePause, 'pause');
			if (this._player.isPlaying() && this._player.getSteps() < 0) {
				L.DomUtil.addClass(this._buttonPlayReversePause, 'fa-pause');
			} else {
				L.DomUtil.removeClass(this._buttonPlayReversePause, 'fa-pause');
			}
		}
	},

	_buttonToStartClicked: function() {
		this._timeDimension.setCurrentTimeIndex(0);
	},

	_buttonToEndClicked: function() {
		console.log(this._timeDimension.options.times);
		this._timeDimension.setCurrentTimeIndex(this._timeDimension.options.times.length);
	},
});

function updateQueryStringParam(key: string, value: number | string): void {
	const url = new URL(window.location.href);
	url.searchParams.set(key, value.toString()); // Add or update the parameter
	// window.history.pushState({}, null, url);
	window.history.replaceState({}, '', url);
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export class TimeDimensionState {
	map: L.Map;
	index: any[];
	paramName: string;

	constructor(map: L.Map, index: any[], paramName: string = 'time') {
		this.map = map;
		this.index = index;
		this.paramName = paramName;
	}

	onTimeChanged(e: Event): void {
		// eslint-disable-next-line no-undef
		// @ts-expect-error  // Need proper type for e
		updateQueryStringParam(this.paramName, this.index[e.time - 1]);
	}

	setup(): void {
		// @ts-expect-error  // Doesn't know map.timeDimension exists.
		this.map.timeDimension.on('timeload', this.onTimeChanged, this);
	}

	fromURL(defaultTime: any): void {
		const url = new URL(window.location.href);
		const theTime = url.searchParams.get(this.paramName) ?? defaultTime;
		console.log('Time from URL:', theTime);
		const timeIndex = this.index.indexOf(theTime);

		console.log('Time from URL:', timeIndex);
		// @ts-expect-error  // Doesn't know map.timeDimension exists.
		this.map.timeDimension.setCurrentTimeIndex(timeIndex);
	}
}
