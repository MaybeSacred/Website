import { Holding } from "./Holding";
export default class Portfolio {
    readonly holdings: Holding[];
    readonly totalValue: number | null;
    readonly name: string;
    readonly description: string;
    constructor(holdings: Holding[], totalValue: number, name: string, description: string) {
        this.holdings = holdings;
        this.totalValue = totalValue;
        this.name = name;
        this.description = description;
    }
}