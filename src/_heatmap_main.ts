import { TDHeatLayer, TDHeatmap, TimeDimensionControl } from './heatmap';

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatmap = TDHeatmap;

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatLayer = TDHeatLayer;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Control.TimeDimensionHeatmap = TimeDimensionControl;
