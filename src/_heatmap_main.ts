import { TDHeatLayer, TDHeatmap, TimeDimensionControl, TimeDimensionState } from './heatmap';

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatmap = TDHeatmap;

// @ts-expect-error  // Doesn't like setting attribute on L
L.TDHeatLayer = TDHeatLayer;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Control.TimeDimensionHeatmap = TimeDimensionControl;

// @ts-expect-error  // Doesn't like setting attribute on L
L.TimeDimensionState = TimeDimensionState;
