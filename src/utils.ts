/**
 * Function to execute promises in serial
 * @param funcs An array of functions, each of which returns a Promise to execute.
 * @returns The results of the Promises.
 */
// eslint-disable-next-line @typescript-eslint/no-unsafe-function-type
export function serial (funcs: Function[]): Promise<[]> {
	return funcs.reduce((promise, func) => promise.then(result => func().then(Array.prototype.concat.bind(result))),
		Promise.resolve([]));
}
