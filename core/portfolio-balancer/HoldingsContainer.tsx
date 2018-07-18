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
	const currentPct = _.sumBy(props.holdings, (x) => x.currentPercentage);
	const desiredPct = _.sumBy(props.holdings, (x) => x.desiredPercentage);
	const computedTotalValue = _.sumBy(
		props.holdings,
		(x) =>
			x.currentShares *
			(props.assets.get(x.assetId) || DefaultIAsset).price,
	);
	return (
		<div>
			<span>Values</span>
			{holdings}
			<span>Total Current Percentage</span>
			<div>{currentPct}</div>
			<span>Total Desired Percentage</span>
			<div>{desiredPct}</div>
			<span>Total Value</span>
			<div>{computedTotalValue}</div>
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(holdingsContainer);
