import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import { updatePortfolioTotalValue } from './actions';
import HoldingDisplayer from './HoldingDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { IAsset, IHolding, IPortfolio } from './types';
interface IProps {
	portfolio: IPortfolio;
	holdings: IHolding[];
	onTotalValueUpdated: (id: Guid, totalPortfolioValue: string) => void;
}
interface IPassableProps {
	portfolioId: Guid;
}
function mapStateToProps(state: IAppState, ownProps: IPassableProps) {
	const portfolio = state.portfolios.get(ownProps.portfolioId);
	if (portfolio === undefined) {
		throw new Error(`${ownProps.portfolioId} not found in portfolios`);
	}
	return {
		portfolio,
		holdings: portfolio.holdings.map((x) => state.holdings.get(x)),
	};
}

const mapDispatchToProps = (dispatch) => ({
	onTotalValueUpdated: (id: Guid, val: string) =>
		dispatch(updatePortfolioTotalValue(id, val)),
});
const formatter = new Intl.NumberFormat(undefined, {
	style: 'currency',
	currency: 'USD',
});
const portfolioContainer = (props: IProps) => {
	const values = [...props.holdings.values()];
	const allocatedValue = _.sumBy(values, (x) => x.currentShares * x.price);
	const totalShares = _.sumBy(values, (x) => x.desiredPercentage);
	const holdings = values.map((x) => {
		return (
			<HoldingDisplayer
				key={x.id}
				holdingId={x.id}
				totalAssetValue={allocatedValue}
				totalPortfolioValue={props.portfolio.totalValue}
				totalShares={totalShares}
			/>
		);
	});
	const desiredPct = _.sumBy(values, (x) => x.desiredPercentage);
	return (
		<div className='container-fluid my-3'>
			<div className='row'>
				<span className='col'>{props.portfolio.name}</span>
				<span className='col'>{props.portfolio.description}</span>
			</div>
			<div className='row'>
				<span className='col-1'>Ticker</span>
				<span className='col-1'>Price</span>
				<span className='col-1'>Current Shares</span>
				<span className='col-1'>Final Shares</span>
				<span className='col-1'>Desired Weight</span>
				<span className='col-1'>Percentage of Assets</span>
				<span className='col-1'>Percentage of Portfolio</span>
				<span className='col'>Notes</span>
				<span className='col'>Press</span>
			</div>
			{holdings}
			<div className='form-row'>
				<span className='col'>Total Weight</span>
				<div className='col'>{desiredPct}</div>
				<span className='col'>Total Value</span>
				<div className='col'>{formatter.format(allocatedValue)}</div>
				<span className='col'>Total Value</span>
				<input
					className='col'
					value={formatter.format(props.portfolio.totalValue)}
					onChange={(event) =>
						props.onTotalValueUpdated(
							props.portfolio.id,
							event.target.value,
						)
					}
				/>
			</div>
		</div>
	);
};
export default connect(
	mapStateToProps,
	mapDispatchToProps,
)(portfolioContainer);
