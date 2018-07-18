import { Guid } from './lib';
import { IAccount, IAsset, IHolding } from './types';
export default interface IAppState {
	accounts: IAccount[];
	holdingIDs: Guid[];
	holdings: IHolding[];
	assets: Map<Guid, IAsset>;
}
