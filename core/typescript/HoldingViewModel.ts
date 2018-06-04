import { Holding, Asset, Guid } from "./Holding";
export class HoldingViewModel {
    symbol: string | null;
    currentPrice: number | null;
    currentShares: number | null;
    desiredPercentage: number | null;
    currentPercentage: number | null;
    desiredShares: number | null;
    description: string;
    constructor(symbol: string, currentPrice: number,
        currentShares: number, desiredPercentage: number,
        currentPercentage: number, desiredShares: number,
        description?: string) {
        this.symbol = symbol;
        this.currentPrice = currentPrice;
        this.currentShares = currentShares;
        this.desiredPercentage = desiredPercentage;
        this.currentPercentage = currentPercentage;
        this.desiredShares = desiredShares;
        this.description = description || "";
    }

}