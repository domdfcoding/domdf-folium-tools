"use strict";
(() => {
  // src/heatmap.ts
  var TDHeatmap = L.TimeDimension.Layer.extend({
    initialize: function(data, options) {
      const heatmapCfg = {
        radius: 15,
        blur: 0.8,
        maxOpacity: 1,
        scaleRadius: false,
        useLocalExtrema: false,
        latField: "lat",
        lngField: "lng",
        valueField: "count",
        defaultWeight: 1,
        ...options.heatmapOptions || {}
      };
      const layer = new HeatmapOverlay(heatmapCfg);
      L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
      this._currentLoadedTime = 0;
      this._currentTimeData = {
        data: []
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
    // @ts-expect-error  // TODO
    _onNewTimeLoading: function(ev) {
      this._getDataForTime(ev.time);
    },
    isReady: function(time) {
      return this._currentLoadedTime === time;
    },
    _update: function() {
      this._baseLayer.setData(this._currentTimeData);
      return true;
    },
    _getDataForTime: function(time) {
      delete this._currentTimeData.data;
      this._currentTimeData.data = [];
      console.log("time=", time);
      const data = Array.prototype.concat(...this.data.slice(0, time));
      for (let i = 0; i < data.length; i++) {
        this._currentTimeData.data.push({
          lat: data[i][0],
          lng: data[i][1],
          count: data[i].length > 2 ? data[i][2] : this.defaultWeight
        });
      }
      this._currentLoadedTime = time;
      if (this._timeDimension && time === this._timeDimension.getCurrentTime() && !this._timeDimension.isLoading()) {
        this._update();
      }
      this.fire("timeload", { time });
    }
  });
  var TDHeatLayer = TDHeatmap.extend({
    initialize: function(data, options) {
      const heatmapCfg = {
        minOpacity: 0.05,
        maxZoom: 18,
        radius: 25,
        blur: 15,
        max: 1,
        ...options.heatmapOptions || {}
      };
      const PatchedHeatLayer = L.HeatLayer.extend({
        redraw: function() {
          if (this._heat && !this._frame && this._map) {
            if (!this._map._animating) {
              this._frame = L.Util.requestAnimFrame(this._redraw, this);
            }
          }
          return this;
        }
      });
      const layer = new PatchedHeatLayer([], heatmapCfg);
      L.TimeDimension.Layer.prototype.initialize.call(this, layer, options);
      this._currentLoadedTime = 0;
      this._currentTimeData = {
        data: []
      };
      this.data = data;
    },
    _update: function() {
      console.log(this._currentTimeData.data);
      this._baseLayer.setLatLngs(this._currentTimeData.data);
      return true;
    }
  });
  var TimeDimensionControl = L.Control.TimeDimension.extend({
    initialize: function(index, options) {
      options.playerOptions = {
        buffer: 1,
        minBufferReady: -1,
        ...options.playerOptions || {}
      };
      L.Control.TimeDimension.prototype.initialize.call(this, options);
      this.index = index;
    },
    _getDisplayDateFormat: function(date) {
      return this.index[date.getTime() - 1];
    }
  });

  // src/_heatmap_main.ts
  L.TDHeatmap = TDHeatmap;
  L.TDHeatLayer = TDHeatLayer;
  L.Control.TimeDimensionHeatmap = TimeDimensionControl;
})();
//# sourceMappingURL=heatmap.js.map
