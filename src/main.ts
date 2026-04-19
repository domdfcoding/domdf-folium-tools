import { MarkerGroup } from './markergroup';
import { PolyMarker } from './polymarker';
import { disableInteraction, enableInteraction, serial } from './utils';
export { disableInteraction, enableInteraction, MarkerGroup, PolyMarker, serial };

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
