/* Based on https://github.com/python-visualization/folium/blob/main/folium/plugins/heat_map_withtime.py
*  Copyright (C) 2013-, Folium developers
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
		if (this.options.backwardButton) {
			this._buttonBackward = this._createButton('Backward', container);
		}
		if (this.options.playReverseButton) {
			this._buttonPlayReversePause = this._createButton('Play Reverse', container);
		}
		if (this.options.playButton) {
			this._buttonPlayPause = this._createButton('Play', container);
		}
		if (this.options.forwardButton) {
			this._buttonForward = this._createButton('Forward', container);
		}
		if (this.options.loopButton) {
			this._buttonLoop = this._createButton('Loop', container);
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
			this._sliderSpeed = this._createSliderSpeed(this.options.styleNS + ' timecontrol-slider timecontrol-speed',
				container);
		}

		this._steps = this.options.timeSteps || 1;

		this._timeDimension.on('timeload', this._update, this);
		this._timeDimension.on('timeload', this._onPlayerStateChange, this);
		this._timeDimension.on('timeloading', this._onTimeLoading, this);

		this._timeDimension.on('limitschanged availabletimeschanged', this._onTimeLimitsChanged, this);

		L.DomEvent.disableClickPropagation(container);

		return container;
	},

	_createSliderSpeed: function(className: string, container: HTMLElement) {
		const sliderContainer = L.DomUtil.create('div', className, container);
		/* L.DomEvent
            .addListener(sliderContainer, 'click', L.DomEvent.stopPropagation)
            .addListener(sliderContainer, 'click', L.DomEvent.preventDefault);
		*/
		const speedLabel = L.DomUtil.create('span', 'speed', sliderContainer);
		const sliderbar = L.DomUtil.create('div', 'slider', sliderContainer);
		const initialSpeed = Math.round(10000 / (this._player.getTransitionTime() || 1000)) / 10;
		speedLabel.innerHTML = this._getDisplaySpeed(initialSpeed);

		// @ts-expect-error  // Doesn't know L.UI namespace exists
		const knob = new L.UI.Knob(sliderbar, {
			step: this.options.speedStep,
			rangeMin: this.options.minSpeed,
			rangeMax: this.options.maxSpeed,
		});

		knob.on('dragend', function(e: L.DragEndEvent) {
			const value = e.target.getValue();
			// @ts-expect-error  // False positive `this` scope
			this._draggingSpeed = false;
			// @ts-expect-error  // False positive `this` scope
			speedLabel.innerHTML = this._getDisplaySpeed(value);
			// @ts-expect-error  // False positive `this` scope
			this._sliderSpeedValueChanged(value);
		}, this);
		knob.on('drag', function(e: Event) {
			// @ts-expect-error  // False positive `this` scope
			this._draggingSpeed = true;
			// @ts-expect-error  // False positive `this` scope
			speedLabel.innerHTML = this._getDisplaySpeed(e.target.getValue());
		}, this);
		knob.on('positionchanged', function(e: Event) {
			// @ts-expect-error  // False positive `this` scope
			speedLabel.innerHTML = this._getDisplaySpeed(e.target.getValue());
		}, this);

		L.DomEvent.on(sliderbar, 'click', function(e: Event) {
			if (e.target === knob._element) {
				return; // prevent value changes on drag release
			}
			// @ts-expect-error  // Doesn't know touches property exists
			const first = e.touches && e.touches.length === 1 ? e.touches[0] : e;
			const x = L.DomEvent.getMousePosition(first, sliderbar).x;
			knob.setPosition(x);
			// @ts-expect-error  // False positive `this` scope
			speedLabel.innerHTML = this._getDisplaySpeed(knob.getValue());
			// @ts-expect-error  // False positive `this` scope
			this._sliderSpeedValueChanged(knob.getValue());
		}, this);
		return knob;
	},

	_onPlayerStateChange: function() {
		if (this._buttonPlayPause) {
			if (this._player.isPlaying() && this._player.getSteps() > 0) {
				L.DomUtil.addClass(this._buttonPlayPause, 'pause');
				L.DomUtil.removeClass(this._buttonPlayPause, 'play');
			} else {
				L.DomUtil.removeClass(this._buttonPlayPause, 'pause');
				L.DomUtil.addClass(this._buttonPlayPause, 'play');
			}
			if (this._player.isWaiting() && this._player.getSteps() > 0) {
				L.DomUtil.addClass(this._buttonPlayPause, 'loading');
			} else {
				this._buttonPlayPause.innerHTML = '';
				L.DomUtil.removeClass(this._buttonPlayPause, 'loading');
			}
		}
		if (this._buttonPlayReversePause) {
			if (this._player.isPlaying() && this._player.getSteps() < 0) {
				L.DomUtil.addClass(this._buttonPlayReversePause, 'pause');
			} else {
				L.DomUtil.removeClass(this._buttonPlayReversePause, 'pause');
			}
			if (this._player.isWaiting() && this._player.getSteps() < 0) {
				L.DomUtil.addClass(this._buttonPlayReversePause, 'loading');
			} else {
				this._buttonPlayReversePause.innerHTML = '';
				L.DomUtil.removeClass(this._buttonPlayReversePause, 'loading');
			}
		}
		if (this._buttonLoop) {
			if (this._player.isLooped()) {
				L.DomUtil.addClass(this._buttonLoop, 'looped');
			} else {
				L.DomUtil.removeClass(this._buttonLoop, 'looped');
			}
		}
		if (this._sliderSpeed && !this._draggingSpeed) {
			let speed = this._player.getTransitionTime() || 1000; // transitionTime
			speed = Math.round(10000 / speed) / 10; // 1s / transition
			this._sliderSpeed.setValue(speed);
		}
	},
});
