/**
 * Function to execute promises in serial
 * @param funcs An array of functions, each of which returns a Promise to execute.
 * @returns The results of the Promises.
 */
// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
export function serial(funcs: Function[]): Promise<[]> {
	return funcs.reduce((promise, func) => promise.then(result => func().then(Array.prototype.concat.bind(result))),
		Promise.resolve([]));
}

export function disableInteraction(map: L.Map, mapElement: HTMLElement) {
	map.dragging.disable();
	map.touchZoom.disable();
	map.doubleClickZoom.disable();
	map.scrollWheelZoom.disable();
	map.boxZoom.disable();
	map.keyboard.disable();
	// if (map.tap) map.tap.disable();
	mapElement.style.cursor = 'default';
}

export function enableInteraction(map: L.Map, mapElement: HTMLElement) {
	map.dragging.enable();
	map.touchZoom.enable();
	map.doubleClickZoom.enable();
	map.scrollWheelZoom.enable();
	map.boxZoom.enable();
	map.keyboard.enable();
	// if (map.tap) map.tap.enable();
	mapElement.style.cursor = 'grab';
}
