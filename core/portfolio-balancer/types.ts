import { Guid, Zero } from './lib';
/** An individual asset such as a stock or bond */
export interface IAsset {
	readonly id: Guid;
	readonly symbol: string;
	readonly price: number;
}
const DefaultIAsset = {
	id: Zero,
	symbol: '',
	price: 0,
};
export { DefaultIAsset };
/**
 * Represents an individual equity or other asset holding
 */
export interface IHolding {
	readonly id: Guid;
	readonly symbol: string;
	readonly price: number;
	readonly currentShares: number;
	readonly desiredPercentage: number;
	readonly description: string;
}
/** A portfolio of holdings */
export interface IPortfolio {
	readonly id: Guid;
	readonly name: string;
	readonly description: string;
	readonly totalValue: number;
	readonly holdings: Guid[];
}
/** Represents a top-level account containing portfolios */
export interface IAccount {
	readonly id: Guid;
	readonly name: string;
	readonly description: string;
	readonly portfolios: Guid[];
}
