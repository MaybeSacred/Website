import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import {
	updateCurrentShares,
	updateDescription,
	updateDesiredPercentage,
	updatePrice,
	updateSymbol,
} from './actions';
import IAppState from './IAppState';
import { Guid } from './lib';
import { IHolding } from './types';
interface IProps {
	holding: IHolding;
	currentPercentage: string;
	desiredShares: string;
	onDesiredPercentageUpdated: (id: Guid, newPct: number) => void;
	onSymbolUpdated: (id: Guid, symbol: string) => void;
	onPriceUpdated: (id: Guid, price: number) => void;
	onCurrentSharesUpdated: (id: Guid, currentShares: number) => void;
	onDescriptionUpdated: (id: Guid, description: string) => void;
}
interface IPassableProps {
	holdingId: Guid;
	totalValue: number;
	totalShares: number;
}
const mapDispatchToProps = (dispatch) => ({
	onDesiredPercentageUpdated: (id: Guid, newPct: number) =>
		dispatch(updateDesiredPercentage(id, newPct)),
	onSymbolUpdated: (id: Guid, symbol: string) =>
		dispatch(updateSymbol(id, symbol)),
	onPriceUpdated: (id: Guid, price: number) =>
		dispatch(updatePrice(id, price)),
	onCurrentSharesUpdated: (id: Guid, currentShares: number) =>
		dispatch(updateCurrentShares(id, currentShares)),
	onDescriptionUpdated: (id: Guid, description: string) =>
		dispatch(updateDescription(id, description)),
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
				onChange={(event) =>
					props.onSymbolUpdated(
						props.holding.id,
						event.target.value,
					)
				}
			/>
			<input
				type='text'
				className='col-1 form-control'
				value={props.holding.price}
				onChange={(event) =>
					props.onPriceUpdated(
						props.holding.id,
						parseFloat(event.target.value),
					)
				}
			/>
			<input
				className='col-1 form-control'
				value={props.holding.currentShares}
				onChange={(event) =>
					props.onCurrentSharesUpdated(
						props.holding.id,
						parseFloat(event.target.value),
					)
				}
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
				onChange={(event) =>
					props.onDescriptionUpdated(
						props.holding.id,
						event.target.value,
					)
				}
			/>
			<button className='col'>Press Me!</button>
		</div>
	);
};

export default connect(
	mapStateToProps,
	mapDispatchToProps,
)(HoldingDisplayer);
