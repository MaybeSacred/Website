import * as _ from 'lodash';
import * as React from 'react';
import { connect } from 'react-redux';
import IAppState from './IAppState';
import { Guid } from './lib';
import PortfolioContainer from './PortfolioContainer';
import { IAccount, IPortfolio } from './types';
interface IProps {
	portfolios: IPortfolio[];
	account: IAccount;
}
function mapStateToProps(state: IAppState) {
	return {
		portfolios: state.portfolioIds.map((x) => state.portfolios.get(x)),
		account: state.account,
	};
}
const accountContainer = (props: IProps) => {
	const values = [...props.portfolios.values()];
	// const totalValue = _.sumBy(
	// 	values,
	// 	(x) =>
	// 		x.currentShares *
	// 		(props.assets.get(x.assetId) || DefaultIAsset).price,
	// );
	const portfolios = values.map((x) => {
		return <PortfolioContainer key={x.id} portfolioId={x.id} />;
	});
	// const desiredPct = _.sumBy(values, (x) => x.desiredPercentage);
	// const computedTotalValue = new Intl.NumberFormat(undefined, {
	// 	style: 'currency',
	// 	currency: 'USD',
	// }).format(totalValue);
	return (
		<div className='container-fluid'>
			<div className='row'>
				<div className='col h4'>{props.account.name}</div>
				<div className='col'>{props.account.description}</div>
			</div>
			{portfolios}
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(accountContainer);
