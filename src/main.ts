import { TDHeatLayer, TDHeatmap, TimeDimensionControl } from './heatmap';
import { MarkerGroup } from './markergroup';
import { PolyMarker } from './polymarker';
import { disableInteraction, enableInteraction, serial } from './utils';
export {
	disableInteraction,
	enableInteraction,
	MarkerGroup,
	PolyMarker,
	serial,
	TDHeatLayer,
	TDHeatmap,
	TimeDimensionControl,
};

// @ts-expect-error  // Doesn't like setting attribute on L
L.PolyMarker = PolyMarker;

// @ts-expect-error  // Doesn't like setting attribute on L
L.MarkerGroup = MarkerGroup;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Util.serial = serial;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Util.disableInteraction = disableInteraction;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Util.enableInteraction = enableInteraction;

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatmap = TDHeatmap;

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatLayer = TDHeatLayer;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Control.TimeDimensionHeatmap = TimeDimensionControl;
