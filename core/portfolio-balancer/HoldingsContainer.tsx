import * as React from 'react';
import { connect } from 'react-redux';
import { HoldingDisplayer } from './HoldingDisplayer';
import IAppState from './IAppState';
import { IHolding } from './types';

interface IProps {
	holdings: IHolding[];
}
function mapStateToProps(state: IAppState) {
	return {
		holdings: state.holdings,
	};
}
const holdingsContainer = (props: IProps) => {
	const holdings = props.holdings.map((x) => {
		return <HoldingDisplayer key={x.id} holding={x} />;
	});
	return (
		<div>
			<span>Values</span>
			{holdings}
		</div>
	);
};
export default connect(
	mapStateToProps,
	{},
)(holdingsContainer);
