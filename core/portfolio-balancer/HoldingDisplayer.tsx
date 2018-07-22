import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import HeldAssetDisplayer from './HeldAssetDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { DefaultIAsset, IAsset, IHolding } from './types';
interface IProps {
	holding: IHolding;
	currentPercentage: string;
	desiredShares: string;
}
interface IPassableProps {
	holdingId: Guid;
	totalValue: number;
	totalShares: number;
}
const mapStateToProps = (state: IAppState, ownProps: IPassableProps) => {
	const holding = state.holdings.get(ownProps.holdingId);
	if (holding === undefined) { throw new Error(`${ownProps.holdingId}`); }
	const asset = state.assets.get(holding.assetId) || DefaultIAsset;
	const currentPercentage =
		(100 * holding.currentShares * asset.price) / ownProps.totalValue;
	const desiredShares =
		((holding.desiredPercentage / ownProps.totalShares) * ownProps.totalValue) / asset.price;
	return {
		holding,
		currentPercentage: currentPercentage.toLocaleString(undefined, {
			minimumFractionDigits: 1,
			maximumFractionDigits: 1,
		}),
		desiredShares: desiredShares.toLocaleString(undefined, {
			minimumFractionDigits: 0,
			maximumFractionDigits: 2,
		}),
	};
};
const HoldingDisplayer = (props: IProps) => {
	return (
		<div className='row'>
			<HeldAssetDisplayer assetId={props.holding.assetId} />
			<input
				className='col-1 form-control'
				value={props.holding.currentShares}
			/>
			<span className='col'>{props.desiredShares}</span>
			<input
				className='col-1 form-control'
				value={props.holding.desiredPercentage}
			/>
			<span className='col'>{props.currentPercentage}</span>
			<input
				className='col form-control'
				value={props.holding.description}
			/>
			<button className='col'>Press Me!</button>
		</div>
	);
};
export default connect(mapStateToProps)(HoldingDisplayer);
