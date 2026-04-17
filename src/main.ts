import { MarkerGroup } from './markergroup';
import { PolyMarker } from './polymarker';
import { serial } from './utils';
export { MarkerGroup, PolyMarker, serial };

// @ts-expect-error  // Doesn't like setting attribute on L
L.PolyMarker = PolyMarker;

// @ts-expect-error  // Doesn't like setting attribute on L
L.MarkerGroup = MarkerGroup;

// @ts-expect-error  // Doesn't like setting attribute on L
L.Util.serial = serial;
