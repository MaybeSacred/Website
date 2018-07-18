import * as React from 'react';
import { IAsset } from './types';
interface IProps {
	asset: IAsset;
}

export const HeldAssetDisplayer = (props: IProps) => {
	return (
		<>
			<span>Asset</span>
			<span>{props.asset.price}</span>
			<input value={props.asset.price} />
			<span>{props.asset.symbol}</span>
			<input value={props.asset.symbol} />
		</>
	);
};
