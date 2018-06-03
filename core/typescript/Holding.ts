import * as fp from "fp-ts";
import * as uuid from "uuid/v4";
import { Option } from "fp-ts/lib/Option";
//import { Option } from "Option";
/**
 * A Guid class reminiscent of the .NET Guid class
 */
export class Guid {
    private readonly zero = "00000000-0000-0000-0000-000000000000";
    readonly value: string;
    private constructor(uuid?: string) {
        this.value = uuid || this.zero;
    }
    /** Creates a new Guid */
    static new() { return new Guid(uuid()); }
}
export module Exchange {
    const AlphaVantageApiKey: string = "ZWUEXDYWYGHIH5R9";
    function lookUpAsset(asset: Asset): Option<Asset> {
        return new fp.option.Some(new Asset(asset.symbol, 100));
        //return fp.option.none;
    }
}
export class Asset {
    readonly symbol: string;
    readonly price: number;
    constructor(symbol: string, price: number) {
        this.symbol = symbol;
        this.price = price;
    }
}
/**
 * Represents an equity or other asset holding
 */
export class Holding {
    readonly id: Guid;
    readonly symbol: Asset;
    readonly currentShares: number;
    readonly desiredPercentage: number;
    readonly description: string;
    constructor(id: Guid, symbol: Asset, desiredPercentage: number, currentShares: number, description?: string) {
        this.id = id;
        this.symbol = symbol;
        this.desiredPercentage = desiredPercentage;
        this.currentShares = currentShares;
        this.description = description || "";

    }
    with(id?: Guid, symbol?: Asset, desiredPercentage?: number, shares?: number, description?: string) {
        return new Holding(id || this.id,
            symbol || this.symbol,
            desiredPercentage || this.desiredPercentage,
            shares || this.currentShares,
            description || this.description);
    }
}