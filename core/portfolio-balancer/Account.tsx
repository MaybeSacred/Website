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
const accountContainer = (props: IProps) => {
	const values = [...props.portfolios.values()];
	const portfolios = values.map((x) => {
		return <HoldingsContainer key={x.id} holdingIds={x.holdings} />;
	});
	return (
		<div className='container-fluid'>
			{portfolios}
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(accountContainer);
