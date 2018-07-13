import * as fp from 'fp-ts';
import { Option } from 'fp-ts/lib/Option';
import * as uuid from 'uuid/v4';
import { Asset } from './Asset';
/**
 * A Guid class reminiscent of the .NET Guid class
 */
export class Guid {
	private readonly zero = '00000000-0000-0000-0000-000000000000';
	public readonly value: string;
	private constructor(uuid?: string) {
		this.value = uuid || this.zero;
	}
	/** Creates a new Guid */
	public static new() {
		return new Guid(uuid());
	}
}
const AlphaVantageApiKey: string = 'ZWUEXDYWYGHIH5R9';
export function lookUpAsset(asset: Asset): Option<Asset> {
	return new fp.option.Some(new Asset(asset.symbol, 100));
	// return fp.option.none;
}

