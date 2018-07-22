import { Guid } from './lib';
import { IAccount, IAsset, IHolding, IPortfolio } from './types';
export default interface IAppState {
	account: IAccount;
	portfolioIds: Guid[];
	portfolios: Map<Guid, IPortfolio>;
	holdingIds: Guid[];
	holdings: Map<Guid, IHolding>;
	assets: Map<Guid, IAsset>;
}
