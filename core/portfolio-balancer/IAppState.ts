import { Guid } from './lib';
import { IHolding } from './types';
export default interface IAppState {
	holdingIDs: string[];
	holdings: IHolding[];
}
