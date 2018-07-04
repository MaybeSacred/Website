import { Asset } from './Asset';
import { Guid } from './lib';
/**
 * Represents an equity or other asset holding
 */
export class Holding {
	public readonly id: Guid;
	public readonly portfolio: string;
	public readonly asset: Asset;
	public readonly currentShares: number;
	public readonly desiredPercentage: number;
	public readonly description: string;
	constructor(
		id: Guid,
		portfolio: string,
		asset: Asset,
		desiredPercentage: number,
		currentShares: number,
		description?: string,
	) {
		this.id = id;
		this.portfolio = portfolio;
		this.asset = asset;
		this.desiredPercentage = desiredPercentage;
		this.currentShares = currentShares;
		this.description = description || '';
	}
	public with(
		id?: Guid,
		portfolio?: string,
		asset?: Asset,
		desiredPercentage?: number,
		shares?: number,
		description?: string,
	) {
		return new Holding(
			id || this.id,
			portfolio || this.portfolio,
			asset || this.asset,
			desiredPercentage || this.desiredPercentage,
			shares || this.currentShares,
			description || this.description,
		);
	}
}
