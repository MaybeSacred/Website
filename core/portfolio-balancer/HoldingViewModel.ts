export class HoldingViewModel {
	public symbol: string | null;
	public currentPrice: number | null;
	public currentShares: number | null;
	public desiredPercentage: number | null;
	public currentPercentage: number | null;
	public desiredShares: number | null;
	public description: string;
	constructor(
		symbol: string,
		currentPrice: number,
		currentShares: number,
		desiredPercentage: number,
		currentPercentage: number,
		desiredShares: number,
		description?: string,
	) {
		this.symbol = symbol;
		this.currentPrice = currentPrice;
		this.currentShares = currentShares;
		this.desiredPercentage = desiredPercentage;
		this.currentPercentage = currentPercentage;
		this.desiredShares = desiredShares;
		this.description = description || '';
	}
}
