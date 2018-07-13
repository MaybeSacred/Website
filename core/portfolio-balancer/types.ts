import { Guid } from './lib';

export interface IAsset {
	readonly id: string;
	readonly symbol: string;
	readonly price: number;
}
/**
 * Represents an equity or other asset holding
 */
export interface IHolding {
	readonly id: string;
	readonly portfolio: string;
	readonly assetId: AssetId;
	readonly currentShares: number;
	readonly desiredShares: number;
	readonly currentPercentage: number;
	readonly desiredPercentage: number;
	readonly description: string;
}
type AssetId = string;
