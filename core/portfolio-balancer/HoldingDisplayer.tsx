import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import * as Actions from './actions';
import IAppState from './IAppState';
import { Guid } from './lib';
import { IHolding } from './types';
// separate out percentage into one for current weight and one for weight in portfolio
// add total value of account, maybe some other aggregates like percentage each asset is of total account value
interface IProps {
	holding: IHolding;
	percentOfAssets: string;
	percentOfPortfolio: string;
	desiredShares: string;
	onDesiredPercentageUpdated: (id: Guid, newPct: string) => void;
	onSymbolUpdated: (id: Guid, symbol: string) => void;
	onPriceUpdated: (id: Guid, price: string) => void;
	onCurrentSharesUpdated: (id: Guid, currentShares: string) => void;
	onDescriptionUpdated: (id: Guid, description: string) => void;
}
interface IPassableProps {
	holdingId: Guid;
	totalAssetValue: number;
	totalPortfolioValue: number;
	totalShares: number;
}
const mapDispatchToProps = (dispatch) => ({
	onDesiredPercentageUpdated: (id: Guid, newPct: string) =>
		dispatch(Actions.updateDesiredPercentage(id, newPct)),
	onSymbolUpdated: (id: Guid, symbol: string) =>
		dispatch(Actions.updateSymbol(id, symbol)),
	onPriceUpdated: (id: Guid, price: string) =>
		dispatch(Actions.updatePrice(id, price)),
	onCurrentSharesUpdated: (id: Guid, currentShares: string) =>
		dispatch(Actions.updateCurrentShares(id, currentShares)),
	onDescriptionUpdated: (id: Guid, description: string) =>
		dispatch(Actions.updateDescription(id, description)),
});
const mapStateToProps = (state: IAppState, ownProps: IPassableProps) => {
	const holding = state.holdings.get(ownProps.holdingId);
	if (holding === undefined) {
		throw new Error(`${ownProps.holdingId} not found in holdings`);
	}
	const percentOfAssets =
		(100 * holding.currentShares * holding.price) /
		ownProps.totalAssetValue;
	const percentOfPortfolio =
		(100 * holding.currentShares * holding.price) /
		ownProps.totalPortfolioValue;
	const desiredShares =
		((holding.desiredPercentage / ownProps.totalShares) *
			ownProps.totalPortfolioValue) /
		holding.price;
	return {
		holding,
		percentOfAssets: percentOfAssets.toLocaleString(undefined, {
			minimumFractionDigits: 1,
			maximumFractionDigits: 1,
		}),
		percentOfPortfolio: percentOfPortfolio.toLocaleString(undefined, {
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
					props.onSymbolUpdated(props.holding.id, event.target.value)
				}
			/>
			<input
				type='text'
				className='col-1 form-control'
				value={props.holding.price}
				onChange={(event) =>
					props.onPriceUpdated(
						props.holding.id,
						event.target.value,
					)
				}
			/>
			<input
				className='col-1 form-control'
				value={props.holding.currentShares}
				onChange={(event) =>
					props.onCurrentSharesUpdated(
						props.holding.id,
						event.target.value,
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
						event.target.value,
					)
				}
			/>
			<span className='col-1 align-bottom'>{props.percentOfAssets}</span>
			<span className='col-1 align-bottom'>
				{props.percentOfPortfolio}
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
