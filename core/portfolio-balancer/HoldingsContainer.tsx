import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import HoldingDisplayer from './HoldingDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { DefaultIAsset, IAsset, IHolding } from './types';
interface IProps {
	holdings: Map<Guid, IHolding>;
	assets: Map<Guid, IAsset>;
}
function mapStateToProps(state: IAppState) {
	return {
		holdings: state.holdings,
		assets: state.assets,
	};
}
const holdingsContainer = (props: IProps) => {
	const values = [...props.holdings.values()];
	const totalValue = _.sumBy(
		values,
		(x) =>
			x.currentShares *
			(props.assets.get(x.assetId) || DefaultIAsset).price,
	);
	const holdings = values.map((x) => {
		return (
			<HoldingDisplayer
				key={x.id}
				holdingId={x.id}
				totalValue={totalValue}
			/>
		);
	});
	const desiredPct = _.sumBy(values, (x) => x.desiredPercentage);
	const computedTotalValue = new Intl.NumberFormat(undefined, {
		style: 'currency',
		currency: 'USD',
	}).format(totalValue);
	return (
		<div className='container-fluid'>
			<span>Values</span>
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
)(holdingsContainer);
