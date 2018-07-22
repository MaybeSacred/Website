import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import HoldingsContainer from './HoldingsContainer';
import IAppState from './IAppState';
import { Guid } from './lib';
import { IPortfolio } from './types';
interface IProps {
	portfolios: IPortfolio[];
}
interface IPassableProps {
	portfolioIds: Guid[];
}
function mapStateToProps(state: IAppState, ownProps: IPassableProps) {
	return {
		portfolios: ownProps.portfolioIds.map((x) => state.portfolios.get(x)),
	};
}
const portfolioContainer = (props: IProps) => {
	const values = [...props.portfolios.values()];
	// const totalValue = _.sumBy(
	// 	values,
	// 	(x) =>
	// 		x.currentShares *
	// 		(props.assets.get(x.assetId) || DefaultIAsset).price,
	// );
	const portfolios = values.map((x) => {
		return <HoldingsContainer key={x.id} holdingIds={x.holdings} />;
	});
	// const desiredPct = _.sumBy(values, (x) => x.desiredPercentage);
	// const computedTotalValue = new Intl.NumberFormat(undefined, {
	// 	style: 'currency',
	// 	currency: 'USD',
	// }).format(totalValue);
	return (
		<div className='container-fluid'>
			{portfolios}
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(portfolioContainer);
