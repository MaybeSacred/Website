import * as React from 'react';
import { HeldAssetDisplayer } from './HeldAssetDisplayer';
import { IAsset, IHolding } from './types';
interface IProps {
	holding: IHolding;
	asset: IAsset;
}

export const HoldingDisplayer = (props: IProps) => {
	return (
		<div className='row'>
			<HeldAssetDisplayer asset={props.asset} />
			<input className='col-1 form-control' value={props.holding.currentShares} />
			<span className='col'>{props.holding.desiredShares}</span>
			<input className='col-1 form-control' value={props.holding.desiredPercentage} />
			<span className='col'>{props.holding.currentPercentage}</span>
			<input className='col form-control' value={props.holding.description} />
			<button className='col'>Press Me!</button>
			<button className='col'>Press Me!</button>
		</div>
	);
};
