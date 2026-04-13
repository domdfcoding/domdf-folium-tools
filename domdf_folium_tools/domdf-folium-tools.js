"use strict";
(() => {
  // src/polymarker.ts
  var PolyMarker = L.Marker.extend({
    // TODO: highlight polygon when marker clicked
    initialize: function(latlng, polyPoints, options) {
      L.Marker.prototype.initialize.call(this, latlng, options);
      this._polygons = [];
      if (polyPoints) {
        polyPoints.forEach((p) => {
          let polygonOptions = {};
          if (options.icon) {
            if ("markerColor" in options.icon.options) {
              polygonOptions = { color: options.icon.options.markerColor };
            }
          }
          this._polygons.push(L.polygon(p, polygonOptions));
        });
      }
    },
    onAdd: function(map) {
      console.log("Add polygon", this._polygon);
      L.Marker.prototype.onAdd.call(this, map);
      if (this._polygons) {
        this._polygons.forEach((p) => {
          p.addTo(map);
        });
      }
      return this;
    },
    onRemove: function(map) {
      console.log("Remove polygon", this._polygon);
      L.Marker.prototype.onRemove.call(this, map);
      if (this._polygons) {
        this._polygons.forEach((p) => {
          p.remove();
        });
      }
      return this;
    }
  });

  // src/markergroup.ts
  var MarkerGroup = L.Layer.extend({
    initialize: function(cluster, _options) {
      console.log("Initialize called");
      this._markers = [];
      this._marker_cluster = cluster;
    },
    addLayers: function(layers) {
      this._markers.push(...layers);
      if (this._map) {
        this._marker_cluster.addLayers(layers);
      }
    },
    onRemove: function(_map) {
      this._map = null;
      console.log("Removing markers", this._markers);
      this._marker_cluster.removeLayers(this._markers);
      return this;
    },
    onAdd: function(map) {
      this._map = map;
      if (this._markers !== void 0) {
        this._marker_cluster.addLayers(this._markers);
      }
      return this;
    }
  });

  // src/utils.ts
  function serial(funcs) {
    return funcs.reduce(
      (promise, func) => promise.then((result) => func().then(Array.prototype.concat.bind(result))),
      Promise.resolve([])
    );
  }
})();
