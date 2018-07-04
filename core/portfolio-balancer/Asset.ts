export class Asset {
	public readonly symbol: string;
	public readonly price: number;
	constructor(symbol: string, price: number) {
		this.symbol = symbol;
		this.price = price;
	}
}
