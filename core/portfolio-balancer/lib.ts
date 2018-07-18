import * as fp from 'fp-ts';
import { Option } from 'fp-ts/lib/Option';
import * as uuid from 'uuid/v4';
import { Opaque } from './Tag';
import { IAsset } from './types';

declare const Uuid4Symbol: unique symbol;
export type Guid = Opaque<string, typeof Uuid4Symbol>;
export function newGuid(): Guid {
	return uuid() as Guid;
}
export const Zero = '00000000-0000-0000-0000-000000000000' as Guid;

const AlphaVantageApiKey: string = 'ZWUEXDYWYGHIH5R9';
// export function lookUpAsset(asset: string): Option<IAsset> {
// 	return new fp.option.Some({ id: '', symbol: asset.symbol, price: 100 });
// 	// return fp.option.none;
// }
