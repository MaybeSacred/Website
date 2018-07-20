import * as React from 'react';
import { IAsset } from './types';
interface IProps {
	asset: IAsset;
}

export const HeldAssetDisplayer = (props: IProps) => {
	return (
		<>
			<span className='col'>Asset: </span>
			<input className='col-1 form-control' value={props.asset.symbol} />
			<input className='col-1 form-control' value={props.asset.price} />
		</>
	);
};
