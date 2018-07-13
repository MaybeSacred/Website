import * as React from 'react';
import { IHolding } from './types';
interface IProps {
	holding: IHolding;
}

export const HoldingDisplayer = (props: IProps) => {
	return (
		<div>
			<input value={props.holding.portfolio} />
			<input value={props.holding.currentShares} />
			<input value={props.holding.desiredShares} />
			<input value={props.holding.currentPercentage} />
			<input value={props.holding.desiredPercentage} />
			<input value={props.holding.description} />
			<button value='Press Me!' />
		</div>
	);
};
