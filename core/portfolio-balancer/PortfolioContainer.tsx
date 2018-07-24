import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import HoldingDisplayer from './HoldingDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { DefaultIAsset, IAsset, IHolding } from './types';
interface IProps {
	holdings: IHolding[];
	assets: Map<Guid, IAsset>;
}
interface IPassableProps {
	holdingIds: Guid[];
}
function mapStateToProps(state: IAppState, ownProps: IPassableProps) {
	return {
		holdings: ownProps.holdingIds.map((x) => state.holdings.get(x)),
		assets: state.assets,
	};
}
const portfolioContainer = (props: IProps) => {
	const values = [...props.holdings.values()];
	const totalValue = _.sumBy(values, (x) => x.currentShares * x.price);
	const totalShares = _.sumBy(values, (x) => x.desiredPercentage);
	const holdings = values.map((x) => {
		return (
			<HoldingDisplayer
				key={x.id}
				holdingId={x.id}
				totalValue={totalValue}
				totalShares={totalShares}
			/>
		);
	});
	const desiredPct = _.sumBy(values, (x) => x.desiredPercentage);
	const computedTotalValue = new Intl.NumberFormat(undefined, {
		style: 'currency',
		currency: 'USD',
	}).format(totalValue);
	return (
		<div className='container-fluid my-3'>
			<div className='row'>
				<span className='col-1'>Ticker</span>
				<span className='col-1'>Price</span>
				<span className='col-1'>Current Shares</span>
				<span className='col-1'>Final Shares</span>
				<span className='col-1'>Desired Weight</span>
				<span className='col-1'>Current Percentage</span>
				<span className='col'>Notes</span>
				<span className='col'>Press</span>
			</div>
			{holdings}
			<div className='row'>
				<span className='col'>Total Desired Percentage</span>
				<div className='col'>{desiredPct}</div>
				<span className='col'>Total Value</span>
				<div className='col'>{computedTotalValue}</div>
			</div>
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(portfolioContainer);
