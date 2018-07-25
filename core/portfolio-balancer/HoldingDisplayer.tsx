import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import { updateDesiredPercentage } from './actions';
import HeldAssetDisplayer from './HeldAssetDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { DefaultIAsset, IAsset, IHolding } from './types';
interface IProps {
	holding: IHolding;
	currentPercentage: string;
	desiredShares: string;
	onDesiredPercentageUpdated: (id: Guid, newPct: number) => void;
}
interface IPassableProps {
	holdingId: Guid;
	totalValue: number;
	totalShares: number;
}
const mapDispatchToProps = (dispatch) => ({
	onDesiredPercentageUpdated: (id: Guid, newPct: number) =>
		dispatch(updateDesiredPercentage(id, newPct)),
});
const mapStateToProps = (state: IAppState, ownProps: IPassableProps) => {
	const holding = state.holdings.get(ownProps.holdingId);
	if (holding === undefined) {
		throw new Error(`${ownProps.holdingId} not found in holdings`);
	}
	const currentPercentage =
		(100 * holding.currentShares * holding.price) / ownProps.totalValue;
	const desiredShares =
		((holding.desiredPercentage / ownProps.totalShares) *
			ownProps.totalValue) /
		holding.price;
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
		<div className='form-row'>
			<input
				type='text'
				className='col-1 form-control'
				value={props.holding.symbol}
			/>
			<input
				type='text'
				className='col-1 form-control'
				value={props.holding.price}
			/>
			<input
				className='col-1 form-control'
				value={props.holding.currentShares}
			/>
			<p className='col-1 align-bottom'>{props.desiredShares}</p>
			<input
				className='col-1 form-control'
				value={props.holding.desiredPercentage}
				onChange={(event) =>
					props.onDesiredPercentageUpdated(
						props.holding.id,
						parseFloat(event.target.value),
					)
				}
			/>
			<span className='col-1 align-bottom'>
				{props.currentPercentage}
			</span>
			<input
				className='col form-control'
				value={props.holding.description}
			/>
			<button className='col'>Press Me!</button>
		</div>
	);
};

export default connect(mapStateToProps, mapDispatchToProps)(HoldingDisplayer);
