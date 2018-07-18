import * as React from 'react';
import { HeldAssetDisplayer } from './HeldAssetDisplayer';
import { IAsset, IHolding } from './types';
interface IProps {
	holding: IHolding;
	asset: IAsset;
}

export const HoldingDisplayer = (props: IProps) => {
	return (
		<div>
			<HeldAssetDisplayer asset={props.asset} />
			<input value={props.holding.currentShares} />
			<input value={props.holding.desiredShares} />
			<input value={props.holding.currentPercentage} />
			<input value={props.holding.desiredPercentage} />
			<input value={props.holding.description} />
			<button>Press Me!</button>
		</div>
	);
};
