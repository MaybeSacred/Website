import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import { HoldingDisplayer } from './HoldingDisplayer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { DefaultIAsset, IAsset, IHolding } from './types';
interface IProps {
	holdings: IHolding[];
	assets: Map<Guid, IAsset>;
}
function mapStateToProps(state: IAppState) {
	return {
		holdings: state.holdings,
		assets: state.assets,
	};
}
const holdingsContainer = (props: IProps) => {
	const holdings = props.holdings.map((x) => {
		return (
			<HoldingDisplayer
				key={x.id}
				holding={x}
				asset={props.assets.get(x.assetId) || DefaultIAsset}
			/>
		);
	});
	const currentPct = new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
	}).format(_.sumBy(props.holdings, (x) => x.currentPercentage));
	const desiredPct = _.sumBy(props.holdings, (x) => x.desiredPercentage);
	const computedTotalValue = new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
	}).format(
		_.sumBy(
			props.holdings,
			(x) =>
				x.currentShares *
				(props.assets.get(x.assetId) || DefaultIAsset).price,
		),
	);
	return (
		<div>
			<span>Values</span>
			{holdings}
			<div className='row'>
				<span className='col-1'>Total Current Percentage</span>
				<div className='col-1'>{currentPct}</div>
				<span className='col-1'>Total Desired Percentage</span>
				<div className='col-1'>{desiredPct}</div>
				<span className='col-1'>Total Value</span>
				<div className='col-1'>{computedTotalValue}</div>
			</div>
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(holdingsContainer);
